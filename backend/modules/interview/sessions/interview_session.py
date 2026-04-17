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
import json
import time
from typing import Any, Dict, Optional

from backend.ai.engines.interview_engine import InterviewEngine
from backend.models.interview import InterviewPhase, InterviewState
from backend.services.audio_buffer import AudioBuffer
from backend.services.interview_persistence import (
    complete_mock_interview,
    fail_mock_interview,
)
from backend.core.evaluation_engine import EvaluationFatalError
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics
from backend.services.redis_manager import redis_client

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
    ):
        """
        Args:
            session_id: Unique WebSocket session identifier (UUID).
            user_id: User identifier from JWT.
            session_policy: Session load policy from the gateway.
            mock_interview_session_id: The session_id stored on the
                MockInterview DB row (returned by /mock-interview/start).
                When provided, results are persisted on completion.
                When None, the session runs without DB write-back
                (e.g. direct WebSocket connections without going through
                the candidate portal flow).
        """
        self.session_id = session_id
        self.user_id = user_id
        self.session_policy = session_policy
        self.mock_interview_session_id = mock_interview_session_id

        self.state = InterviewState()
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

    # ------------------------------------------------------------------

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming WebSocket message.

        Returns a response dict to send back, or None.
        """
        # --- STATELESS ARCHITECTURE ---
        # Hydrate session block dynamically from Redis if resuming.
        try:
            persisted = await redis_client.get_session_state_obj(self.session_id)
            if persisted:
                self.state, self.eval_context_cache = persisted
        except Exception as e:
            logger.warning(f"Could not load state from redis: {e}")

        msg_type = self._get_message_type(message)

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

        if msg_type == "ping":
            response = await self._handle_ping()
        elif msg_type == "resume_upload":
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
            
        # --- STATELESS ARCHITECTURE ---
        # Persist updated session block to Redis 
        try:
            await redis_client.save_session_state_obj(self.session_id, (self.state, self.eval_context_cache))
        except Exception as e:
            logger.error(f"Failed to persist state to redis: {e}")
            
        return response

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
            with contextlib.suppress(asyncio.CancelledError):
                await self._early_eval_task
            self._early_eval_task = None

        # Mark abandoned if we have a DB row and didn't complete normally
        if self.mock_interview_session_id and not self._completed_normally:
            await fail_mock_interview(self.mock_interview_session_id, "session_cleanup")

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

    async def _handle_resume_upload(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resume_upload message.

        Expected format:
            {"type": "resume_upload", "file_name": "...", "file_bytes": "<b64>"}
        """
        self.state.transition_to(InterviewPhase.PROCESSING_RESUME)

        data = message.get("data", {})
        file_name = data.get("file_name", "")
        file_bytes = data.get("file_bytes", "")

        if not file_name or not file_bytes:
            return {
                "type": "error",
                "code": "INVALID_PAYLOAD",
                "message": "Missing file_name or file_bytes",
                "recoverable": True,
            }

        logger.info("Resume upload message received, starting processing.")
        try:
            result = await self.engine.start_interview(
                state=self.state,
                file_name=file_name,
                file_bytes_b64=file_bytes,
                session_policy=self.session_policy,
            )
            logger.info("Interview engine returned initial question.")
        except Exception:
            logger.exception("Bootstrap interview failed in session handler")
            return {
                "type": "error",
                "message": "Failed to process resume",
                "recoverable": True,
            }

        return result

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

        # Evaluate the answer
        try:
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
                return {
                    "type": "next_question",
                    "question": eval_result,
                    "next_question": next_q,
                }

        # ----------------------------------------------------------------
        # Interview complete - generate final report and persist to DB
        # ----------------------------------------------------------------
        final_result = await self.engine.complete_interview(self.state)

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
