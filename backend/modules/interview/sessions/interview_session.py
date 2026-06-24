"""
Interview Session Manager - Handles interview lifecycle and message routing.

Changes vs previous version:
- __init__ now accepts an optional mock_interview_session_id so the gateway
  can pass the session_id that was stored in the MockInterview row.
- _handle_stream_end calls interview_persistence.complete_mock_interview()
  once the final report is ready.
- cleanup() calls interview_persistence.fail_mock_interview() when the
  session ends without having completed normally, so rows don't stay
  stuck in 'in_progress'.
"""

import asyncio
import contextlib
import concurrent.futures
import json
import time
from typing import Any, Dict, Optional, Set
from sqlalchemy import select

from backend.ai.engines.interview_engine import InterviewEngine
from backend.modules.interview.models import InterviewPhase, InterviewState
from backend.services.audio_buffer import AudioBuffer
from backend.modules.interview.persistence import (
    complete_mock_interview,
    fail_mock_interview,
)
from backend.core.telemetry import SessionTelemetry
from backend.core.evaluation_engine import EvaluationFatalError
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics
from backend.services.redis_manager import redis_client
from backend.infrastructure.database.database import AsyncSessionLocal
from backend.models.candidate_portal import CandidateProfile

logger = get_logger(__name__)


class InterviewSession:
    """
    Manages a single interview session lifecycle.

    Responsibilities:
    - Route messages to appropriate handlers
    - Manage interview state machine
    - Buffer audio chunks
    - Coordinate with InterviewEngine
    - Persist results to MockInterview table on completion/error
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        session_policy: Dict[str, Any],
        mock_interview_session_id: Optional[str] = None,
        broadcast_callback: Optional[callable] = None,
    ):
        """
        Args:
            session_id: Unique WebSocket session identifier (UUID).
            user_id: User identifier from JWT.
            session_policy: Session load policy from the gateway.
            mock_interview_session_id: The session_id stored on the
                MockInterview DB row (returned by /mock-interview/start).
            broadcast_callback: A function that will be called when the phase changes
                to broadcast the event to the frontend.
        """
        self.session_id = session_id
        self.user_id = user_id
        self.session_policy = session_policy
        self.mock_interview_session_id = mock_interview_session_id
        self.broadcast_callback = broadcast_callback

        self.state = InterviewState(user_id=self.user_id, session_id=self.session_id)
        if self.broadcast_callback:
            self.state.subscribe_to_phase_changes(self.broadcast_callback)

        self.engine = InterviewEngine()
        self.audio_buffer = AudioBuffer(session_id=self.session_id)
        self.eval_context_cache: Dict[int, dict] = {}

        # Set when the interview completes normally so cleanup() knows
        # not to mark the row as abandoned.
        self._completed_normally: bool = False

        # Audio streaming state
        self._first_chunk_time: Optional[float] = None
        self._last_chunk_time: Optional[float] = None
        self._last_partial_at: float = 0.0
        self._partial_transcript: str = ""
        self._partial_count: int = 0
        self._early_eval_task: Optional[asyncio.Task] = None
        
        # Internal error flag to distinguish between engine failures 
        # and user abandonment.
        self._internal_error: bool = False

        # Monotonic sequence counter for backend -> frontend messages
        self._next_seq: int = 1
        self._dirty: bool = False
        
        # Background task tracking for cleanup
        self.tasks: Set[asyncio.Task] = set()
        
        # Async safety serialization lock
        self._processing_lock = asyncio.Lock()

    def get_next_seq(self) -> int:
        """Increment and return the next sequence ID."""
        seq = self._next_seq
        self._next_seq += 1
        return seq

    # ------------------------------------------------------------------

    async def hydrate(self) -> bool:
        """
        Explicitly hydrate session state from Redis.
        Returns True if state was found and loaded.
        """
        try:
            persisted = await redis_client.get_session_state_obj(self.session_id)
            if persisted:
                # SECURITY CHECK: Ensure user_id matches
                if persisted[0].user_id and persisted[0].user_id != self.user_id:
                    logger.warning(
                        f"Security rejection: Session {self.session_id} belongs to user {persisted[0].user_id}, "
                        f"but user {self.user_id} tried to hydrate it."
                    )
                    return False

                self.state, self.eval_context_cache = persisted
                self.state.session_id = self.session_id
                # Re-attach broadcast callback after hydration
                if self.broadcast_callback:
                    self.state.subscribe_to_phase_changes(self.broadcast_callback)
                logger.info(f"Session {self.session_id} hydrated from Redis.")
                return True
        except Exception as e:
            logger.warning(f"Could not hydrate session {self.session_id}: {e}")
        return False

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming WebSocket message.

        Returns a response dict to send back, or None.
        """
        msg_type = self._get_message_type(message)

        if msg_type == "ping":
            return await self._handle_ping()

        if self._processing_lock.locked():
            logger.warning(f"Session {self.session_id} is already processing a message. Dropping concurrent input.")
            return {"type": "error", "message": "Please wait, the interviewer is thinking.", "recoverable": True}

        async with self._processing_lock:
            # --- STATELESS ARCHITECTURE ---
            # Hydrate session block dynamically from Redis if resuming.
            await self.hydrate()

            # Risk 1: Validate session still exists in registry before any heavy logic
            from backend.modules.interview.sessions.registry import get_session_registry
            registry = get_session_registry()
            if not await registry.get_metadata(self.session_id):
                logger.warning(f"Aborting handle_message for {self.session_id}: session no longer in registry.")
                return None

            if not self.state.can_proceed(msg_type):
                logger.warning(
                    f"Invalid message {msg_type} for phase {self.state.phase.value}",
                    extra={"extra_data": {"session_id": self.session_id}},
                )
                response = {
                    "type": "error",
                    "code": "INVALID_STATE",
                    "message": f"Cannot receive {msg_type} in {self.state.phase.value} phase",
                    "recoverable": True,
                }
                return response

            if msg_type == "resume_upload":
                response = await self._handle_resume_upload(message)
            elif msg_type == "audio_chunk":
                response = await self._handle_audio_chunk(message)
            elif msg_type in ("stream_end", "audio_end"):
                response = await self._handle_stream_end(message)
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                response = {
                    "type": "error",
                    "code": "UNKNOWN_MESSAGE",
                    "message": f"Unknown message type: {msg_type}",
                    "recoverable": True,
                }
                
            # --- LAZY PERSISTENCE ---
            # Only persist to Redis if the state was marked as dirty (changed)
            if self._dirty:
                # Check registry one last time to prevent ghost updates after disconnect/cleanup
                if await registry.get_metadata(self.session_id):
                    try:
                        await redis_client.save_session_state_obj(self.session_id, (self.state, self.eval_context_cache))
                        self._dirty = False # Reset flag after successful save
                    except Exception as e:
                        logger.error(f"Failed to persist state to redis: {e}")
                else:
                    logger.warning(f"Skipping Redis save for {self.session_id}: session already unregistered.")
                
            return response

    async def persist_state_now(self) -> None:
        """
        Persist the current state immediately.

        Used by gateway-owned phase transitions so the next incoming message
        hydrates the latest phase without race windows.
        """
        try:
            await redis_client.save_session_state_obj(
                self.session_id, (self.state, self.eval_context_cache)
            )
            self._dirty = False
        except Exception as e:
            logger.warning(f"Immediate state persist failed for {self.session_id}: {e}")

    async def cleanup(self) -> None:
        """
        Clean up session resources.

        If the interview did not complete normally and we have a
        mock_interview_session_id, the DB row is marked as abandoned
        so it doesn't stay stuck in 'in_progress'.

        Also explicitly deletes all Redis keys scoped to this session
        to prevent zombie state from lingering.
        """
        logger.info(
            "Cleaning up interview session",
            extra={"extra_data": {"session_id": self.session_id}},
        )

        # Cancel any pending tasks
        if self._early_eval_task and not self._early_eval_task.done():
            self._early_eval_task.cancel()
            self._early_eval_task = None
            
        for task in list(self.tasks):
            if not task.done():
                task.cancel()
        
        if self.tasks:
            # Wait briefly for tasks to acknowledge cancellation
            with contextlib.suppress(asyncio.CancelledError, concurrent.futures.CancelledError):
                await asyncio.gather(*self.tasks, return_exceptions=True)
            self.tasks.clear()

        # Mark abandoned if we have a DB row and didn't complete normally OR crash
        if self.mock_interview_session_id and not self._completed_normally:
            reason = "internal_error" if self._internal_error else "session_cleanup"
            await fail_mock_interview(self.mock_interview_session_id, reason)

        # ── Redis zombie state cleanup ──
        # Delete all session-scoped keys so they don't linger until TTL expiry.
        try:
            await redis_client.clear_session_state(self.session_id)
            await redis_client.clear_cache(self.session_id)
            # Clear the pickled state object (binary client)
            await redis_client.redis_bin.delete(
                f"interview:state_obj:{self.session_id}"
            )
            logger.debug(
                "Redis keys cleaned for session",
                extra={"extra_data": {"session_id": self.session_id}},
            )
        except Exception as e:
            logger.warning(f"Redis cleanup error for {self.session_id}: {e}")

        self.state.reset()
        self.audio_buffer.clear()
        self.eval_context_cache.clear()

    # ==================== Message Handlers ====================

    async def _handle_ping(self) -> Dict[str, Any]:
        return {"type": "pong"}

    async def _handle_resume_upload(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle resume_upload message.

        Expected format:
            {"type": "resume_upload", "file_name": "...", "file_bytes": "<b64>"}
        """
        if getattr(self.state, "resume_processed", False):
            logger.info("Resume already processed for this session; ignoring duplicate upload")
            return None
        if getattr(self.state, "resume_processing", False):
            logger.info("Resume processing already in progress for this session; ignoring duplicate upload")
            return {
                "type": "system_message",
                "code": "RESUME_PROCESSING",
                "text": "Your resume is already being processed.",
                "recoverable": True,
            }

        self.state.resume_processing = True
        self.state.transition_to(InterviewPhase.PROCESSING_RESUME)
        self._dirty = True
        await self.persist_state_now()
        
        data = message.get("data", {})
        file_name = data.get("file_name", "")
        file_bytes = data.get("file_bytes", "")

        SessionTelemetry.record(self.session_id, "RESUME_UPLOAD_STARTED", metadata={"file_name": file_name})

        if not file_name or not file_bytes:
            return {
                "type": "error",
                "code": "INVALID_PAYLOAD",
                "message": "Missing file_name or file_bytes",
                "recoverable": True,
            }

        # Cost-safety guard: if profile resume is already parsed, reuse it.
        cached_profile = await self._load_profile_resume_data()
        if cached_profile is not None:
            logger.info("Using cached profile resume data; skipping duplicate resume parsing.")
            try:
                result = await self.engine.start_interview_from_profile(
                    state=self.state,
                    profile_data=cached_profile,
                    session_policy=self.session_policy,
                    session_id=self.session_id,
                )
                SessionTelemetry.record(self.session_id, "RESUME_PARSE_COMPLETED", metadata={"cached": True})
                self.state.resume_processed = True
                self.state.resume_processing = False
                self._dirty = True
                return result
            except Exception:
                logger.exception("Failed to start interview from cached profile data")

        logger.info("Resume upload message received, starting processing.")
        try:
            result = await self.engine.start_interview(
                state=self.state,
                file_name=file_name,
                file_bytes_b64=file_bytes,
                session_policy=self.session_policy,
            )
            SessionTelemetry.record(self.session_id, "RESUME_PARSE_COMPLETED", metadata={"cached": False})
            self.state.resume_processed = True
            self.state.resume_processing = False
            logger.info("Interview engine returned initial question.")
            SessionTelemetry.record(self.session_id, "QUESTION_GENERATED", metadata={"question_index": 0})
            self._dirty = True
        except Exception as e:
            logger.exception("Bootstrap interview failed in session handler")
            self._internal_error = True
            self.state.resume_processing = False
            self.state.transition_to(InterviewPhase.WAITING_RESUME)
            self._dirty = True
            return {
                "type": "error",
                "code": "ENGINE_CRASH",
                "message": f"Interview engine failed: {str(e)}",
                "recoverable": False,
            }

        return result

    async def _load_profile_resume_data(self) -> Optional[Dict[str, Any]]:
        """
        Load already-parsed resume profile data from CandidateProfile.
        Returns None when no reusable profile is available.
        """
        try:
            async with AsyncSessionLocal() as db:
                res = await db.execute(
                    select(CandidateProfile).filter(CandidateProfile.user_id == self.user_id)
                )
                profile = res.scalar_one_or_none()
                if not profile:
                    return None
                if not profile.resume_url:
                    return None

                skills: list[str] = []
                if profile.skills:
                    try:
                        parsed_skills = json.loads(profile.skills)
                        if isinstance(parsed_skills, list):
                            skills = [str(s) for s in parsed_skills if isinstance(s, str)]
                    except Exception:
                        skills = []

                return {
                    "name": profile.name,
                    "skills": skills,
                    "projects": [],
                }
        except Exception:
            logger.exception("Failed to load candidate profile resume data")
            return None

    async def _handle_audio_chunk(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Buffer an incoming audio chunk and emit partial transcripts when
        enough audio has accumulated.
        """
        audio_chunk = message.get("bytes")

        if not audio_chunk:
            return None

        now = time.time()
        if self._first_chunk_time is None:
            self._first_chunk_time = now
            SessionTelemetry.record(self.session_id, "AUDIO_STREAM_STARTED")
        self._last_chunk_time = now

        if not self.audio_buffer.add(audio_chunk):
            logger.warning(
                "Audio buffer overflow",
                extra={"extra_data": {"session_id": self.session_id}},
            )
            metrics.increment_counter("audio_buffer_overflow")
            self.audio_buffer.clear()
            self._partial_transcript = ""
            self._partial_count = 0
            return {
                "type": "error",
                "code": "AUDIO_BUFFER_FULL",
                "message": "Audio too long. Please send a shorter response.",
                "recoverable": True,
            }

        partial_min_bytes = 12000
        partial_interval = 0.9

        if (
            len(self.audio_buffer) >= partial_min_bytes
            and (now - self._last_partial_at) >= partial_interval
        ):
            self._last_partial_at = now

            from backend.core.celery_tasks import transcribe_audio_task
            
            filepath = self.audio_buffer.filepath
            suffix = self.engine._detect_audio_suffix(self.audio_buffer.bytes())

            # Fire and forget asynchronous task
            transcribe_audio_task.delay(filepath, suffix, self.session_id)

        return None

    async def _handle_stream_end(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the complete answer, evaluate it, and either generate the
        next question or complete the interview.

        On final completion, writes results back to the MockInterview row.
        """
        if not self.state.questions or self.state.current_index >= len(self.state.questions):
            return {
                "type": "error",
                "code": "INVALID_STATE",
                "message": "No active question to evaluate.",
                "recoverable": True,
            }
        question = self.state.questions[self.state.current_index]
        audio_bytes = self.audio_buffer.bytes()
        SessionTelemetry.record(self.session_id, "STREAM_END", metadata={"buffer_bytes": len(audio_bytes)})

        # Evaluate the answer
        try:
            SessionTelemetry.record(self.session_id, "EVALUATION_STARTED", metadata={"question_index": self.state.current_index})
            eval_result = await self.engine.evaluate_answer(
                state=self.state,
                audio_bytes=audio_bytes,
                transcript=self._partial_transcript or "",
                question=question,
                session_policy=self.session_policy,
                eval_context_cache=self.eval_context_cache,
                draft_transcript=self._partial_transcript,
                early_eval_task=self._early_eval_task,
            )
        except EvaluationFatalError:
            logger.warning(f"EvaluationFatalError raised for session {self.session_id}. Requesting candidate repeat.")
            return {
                "type": "system_message",
                "text": "I didn't quite catch the logic in that response. Could you explain it one more time?",
            }
        except Exception as e:
            logger.exception("Evaluation failed in session handler")
            self._internal_error = True
            return {
                "type": "error",
                "code": "ENGINE_CRASH",
                "message": "Interview processing failed",
                "recoverable": False,
            }
        finally:
            self._dirty = True


        # Reset audio state
        self.audio_buffer.clear()
        self._first_chunk_time = None
        self._last_chunk_time = None
        self._partial_transcript = ""
        self._partial_count = 0

        # Continue or complete?
        if self.engine._should_continue(self.state):
            last_eval = eval_result.get("data", {}).get("evaluation", {})
            next_q = await self.engine.generate_next_question(
                state=self.state,
                last_evaluation=last_eval,
                session_policy=self.session_policy,
            )

            if next_q:
                SessionTelemetry.record(self.session_id, "QUESTION_GENERATED", metadata={"question_index": self.state.current_index})
                return {
                    "type": "next_question",
                    "question": eval_result,
                    "next_question": next_q,
                }

        # ----------------------------------------------------------------
        # Interview complete - generate final report and persist to DB
        # ----------------------------------------------------------------
        final_result = await self.engine.complete_interview(self.state)
        SessionTelemetry.record(self.session_id, "SESSION_COMPLETED")

        # Persist to MockInterview table if we have a session_id
        if self.mock_interview_session_id:
            await complete_mock_interview(
                self.mock_interview_session_id,
                final_result.get("report", {}),
                self.state.answers,
            )
            self._completed_normally = True

        return {
            "type": "complete",
            "evaluation": eval_result,
            "final": final_result,
        }

    # ==================== Helper Methods ====================

    def _get_message_type(self, message: Dict[str, Any]) -> str:
        """Extract message type from a WebSocket message dict."""
        text = message.get("text")
        if text:
            try:
                data = json.loads(text)
                return data.get("type", "unknown")
            except json.JSONDecodeError:
                pass

        if isinstance(message.get("data"), dict):
            return message.get("data", {}).get("type", "unknown")

        if message.get("bytes"):
            return "audio_chunk"

        return "unknown"

    @property
    def phase(self) -> InterviewPhase:
        return self.state.phase

    @property
    def is_complete(self) -> bool:
        return self.state.phase == InterviewPhase.COMPLETE
