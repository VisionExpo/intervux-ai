"""
Interview Session Manager - Handles interview lifecycle and message routing.

This class manages:
- Interview state machine transitions
- Message routing to engine
- Audio buffering
- Session cleanup
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional

from backend.engines.interview_engine import InterviewEngine
from backend.models.interview import InterviewPhase, InterviewState
from backend.services.audio_buffer import AudioBuffer
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)


class InterviewSession:
    """
    Manages a single interview session lifecycle.
    
    Responsibilities:
    - Route messages to appropriate handlers
    - Manage interview state machine
    - Buffer audio chunks
    - Coordinate with InterviewEngine
    """

    def __init__(
        self,
        session_id: str,
        user_id: str,
        session_policy: Dict[str, Any],
    ):
        """
        Initialize interview session.
        
        Args:
            session_id: Unique session identifier
            user_id: User identifier from JWT
            session_policy: Session load policy
        """
        self.session_id = session_id
        self.user_id = user_id
        self.session_policy = session_policy
        
        self.state = InterviewState()
        self.engine = InterviewEngine()
        self.audio_buffer = AudioBuffer()
        self.eval_context_cache: Dict[int, dict] = {}
        
        # Audio streaming state
        self._first_chunk_time: Optional[float] = None
        self._last_chunk_time: Optional[float] = None
        self._last_partial_at: float = 0.0
        self._partial_transcript: str = ""
        self._partial_count: int = 0
        self._early_eval_task: Optional[asyncio.Task] = None

    async def handle_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle incoming WebSocket message.
        
        Args:
            message: WebSocket message dict with 'type', 'text', 'bytes', etc.
            
        Returns:
            Response dict to send back, or None
        """
        msg_type = self._get_message_type(message)
        
        # Guard: Check if message is allowed in current phase
        if not self.state.can_proceed(msg_type):
            logger.warning(
                f"Invalid message {msg_type} for phase {self.state.phase.value}",
                extra={"extra_data": {"session_id": self.session_id}}
            )
            return {
                "type": "error",
                "code": "INVALID_STATE",
                "message": f"Cannot receive {msg_type} in {self.state.phase.value} phase",
                "recoverable": True,
            }
        
        # Route to appropriate handler
        if msg_type == "ping":
            return await self._handle_ping()
            
        elif msg_type == "resume_upload":
            return await self._handle_resume_upload(message)
            
        elif msg_type == "audio_chunk":
            return await self._handle_audio_chunk(message)
            
        elif msg_type in ("stream_end", "audio_end"):
            return await self._handle_stream_end(message)
            
        else:
            logger.warning(f"Unknown message type: {msg_type}")
            return {
                "type": "error",
                "code": "UNKNOWN_MESSAGE",
                "message": f"Unknown message type: {msg_type}",
                "recoverable": True,
            }

    async def cleanup(self) -> None:
        """Clean up session resources."""
        logger.info(
            "Cleaning up interview session",
            extra={"extra_data": {"session_id": self.session_id}}
        )
        
        # Cancel any pending tasks
        if self._early_eval_task and not self._early_eval_task.done():
            self._early_eval_task.cancel()
        
        # Reset state
        self.state.reset()
        self.audio_buffer.clear()
        self.eval_context_cache.clear()

    # ==================== Message Handlers ====================

    async def _handle_ping(self) -> Dict[str, Any]:
        """Handle ping message."""
        return {"type": "pong"}

    async def _handle_resume_upload(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle resume upload message.
        
        Expected message format:
        {
            "type": "resume_upload",
            "file_name": "resume.pdf",
            "file_bytes": "base64..."
        }
        """
        self.state.transition_to(InterviewPhase.WAITING_RESUME)
        
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
        
        try:
            # Start interview with resume
            result = await self.engine.start_interview(
                state=self.state,
                file_name=file_name,
                file_bytes_b64=file_bytes,
                session_policy=self.session_policy,
            )
        except Exception:
            logger.exception("Bootstrap interview failed")
            return {
                "type": "error",
                "message": "Failed to process resume",
                "recoverable": True,
            }
        
        return result

    async def _handle_audio_chunk(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming audio chunk.
        
        Expected message format:
        {
            "bytes": <binary audio data>
        }
        
        Returns partial transcript if enough audio accumulated.
        """
        audio_chunk = message.get("bytes")
        
        if not audio_chunk:
            return None
        
        # Add to buffer
        now = time.time()
        if self._first_chunk_time is None:
            self._first_chunk_time = now
        self._last_chunk_time = now
        
        self.audio_buffer.add(audio_chunk)
        
        # Check if we should emit partial transcript
        partial_min_bytes = 12000
        partial_interval = 0.9
        
        if (len(self.audio_buffer) >= partial_min_bytes and 
            (now - self._last_partial_at) >= partial_interval):
            
            self._last_partial_at = now
            
            # Transcribe partial audio
            from functools import partial
            from backend.services.stt_service import transcribe_audio_bytes
            
            partial_text = await asyncio.to_thread(
                partial(
                    transcribe_audio_bytes,
                    audio_bytes=self.audio_buffer.bytes(),
                    suffix=self.engine._detect_audio_suffix(self.audio_buffer.bytes()),
                )
            )
            
            if partial_text:
                self._partial_transcript = partial_text
                self._partial_count += 1
                metrics.increment_counter("partial_transcript_count")
                
                return {
                    "type": "partial_transcript",
                    "text": partial_text,
                }
        
        return None

    async def _handle_stream_end(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle stream end - process complete answer.
        
        Returns evaluation and next question (if any).
        """
        # Get current question
        question = self.state.questions[self.state.current_index]
        
        # Process audio
        audio_bytes = self.audio_buffer.bytes()
        
        # Send processing phase
        processing_response = {
            "type": "phase",
            "value": "PROCESSING",
        }
        
        # Evaluate answer
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
        
        # Reset audio state
        self.audio_buffer.clear()
        self._first_chunk_time = None
        self._last_chunk_time = None
        self._partial_transcript = ""
        self._partial_count = 0
        
        # Check if we should continue
        if self.engine._should_continue(self.state):
            # Generate next question
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
        
        # Complete interview
        final_result = await self.engine.complete_interview(self.state)
        
        return {
            "type": "complete",
            "evaluation": eval_result,
            "final": final_result,
        }

    # ==================== Helper Methods ====================

    def _get_message_type(self, message: Dict[str, Any]) -> str:
        """Extract message type from message."""
        # Check text payload
        text = message.get("text")
        if text:
            try:
                data = json.loads(text)
                return data.get("type", "unknown")
            except json.JSONDecodeError:
                pass
        
        # Check data key
        if isinstance(message.get("data"), dict):
            return message.get("data", {}).get("type", "unknown")
        
        # Check bytes - this is audio chunk
        if message.get("bytes"):
            return "audio_chunk"
        
        return "unknown"

    @property
    def phase(self) -> InterviewPhase:
        """Get current phase."""
        return self.state.phase

    @property
    def is_complete(self) -> bool:
        """Check if interview is complete."""
        return self.state.phase == InterviewPhase.COMPLETE

