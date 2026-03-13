"""
WebSocket Gateway - Thin network I/O layer for interview WebSocket.

This is the entry point for WebSocket connections. It handles:
- JWT token verification
- Rate limiting
- Session slot management
- Connection lifecycle

All AI logic is delegated to InterviewSession/InterviewEngine.
"""

import asyncio
import json
import os
import time
import uuid
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.auth.jwt_service import verify_token, TokenData
from backend.models.interview import InterviewPhase
from backend.sessions.interview_session import InterviewSession
from backend.sessions.registry import get_session_registry
from backend.services.tts_service import synthesize_speech_with_visemes
from backend.services.viseme_service import VisemeService
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)
viseme_service = VisemeService()


class InterviewGateway:
    """
    WebSocket gateway for interview sessions.
    
    Responsibilities:
    - Network I/O only (thin layer)
    - JWT token verification
    - Rate limiting
    - Session slot management
    - Message routing to session
    """

    def __init__(self, total_questions: int = 2):
        """
        Initialize gateway.
        
        Args:
            total_questions: Default number of questions per interview
        """
        self.total_questions = total_questions
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_WS_PER_MINUTE", "30"))
        self.receive_timeout_s = int(os.getenv("WS_RECEIVE_TIMEOUT_S", "120"))
        self.send_timeout_s = int(os.getenv("WS_SEND_TIMEOUT_S", "20"))
        
        self._session_lock = asyncio.Lock()
        self._rate_limit_lock = asyncio.Lock()
        self._active_sessions = 0
        self._pending_connections = 0
        self._connections: Set[WebSocket] = set()
        self._ip_hits: Dict[str, list] = {}
        self._registry = get_session_registry()

    async def handle(self, ws: WebSocket) -> None:
        """
        Handle a new WebSocket connection.
        
        This is the main entry point for WebSocket connections.
        """
        # Verify JWT token
        token = ws.query_params.get("token")
        if not token:
            await ws.accept()
            await self._send_error(
                ws,
                "UNAUTHORIZED",
                "Missing authentication token",
                recoverable=True,
            )
            await self._close_ws(ws, code=1008)
            return
        
        try:
            user_data: TokenData = verify_token(token)
        except Exception:
            await ws.accept()
            await self._send_error(
                ws,
                "UNAUTHORIZED",
                "Invalid authentication token",
                recoverable=True,
            )
            await self._close_ws(ws, code=1008)
            return

        # Check rate limit
        client_ip = self._client_ip(ws)
        if not await self._allow_ip(client_ip):
            await ws.accept()
            await self._send_error(
                ws,
                "RATE_LIMITED",
                "Too many connection attempts from this IP.",
                recoverable=True,
            )
            await self._close_ws(ws, code=1008)
            metrics.increment_counter("rate_limit_rejections")
            return

        # Accept connection
        await ws.accept()
        
        # Debug logs for tracking WebSocket flow
        try:
            logger.info("Socket accepted")
            logger.info(f"User authenticated: {user_data.user_id}")
        except Exception as e:
            logger.exception("Error in debug logs", exc_info=e)
        
        await self._mark_pending(delta=1)
        
        # Try to acquire session slot
        if not await self._try_acquire_session_slot():
            await self._mark_pending(delta=-1)
            await self._send_error(
                ws,
                "SERVER_OVERLOADED",
                "Server is at capacity. Try again shortly.",
                recoverable=False,
            )
            await self._close_ws(ws, code=1013)
            return
        
        await self._mark_pending(delta=-1)

        # Create session
        session_id = str(uuid.uuid4())
        session_policy = self._build_load_policy()
        
        session = InterviewSession(
            session_id=session_id,
            user_id=user_data.user_id,
            session_policy=session_policy,
        )
        
        await self._registry.register(session_id, session)
        
        self._connections.add(ws)
        
        metrics.record_gauge("queue_depth", self._pending_connections)
        metrics.record_gauge("active_sessions", self._active_sessions)

        logger.info(
            "WebSocket session started",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "active_sessions": self._active_sessions,
                    "policy": session_policy,
                }
            },
        )

        try:
            # Send welcome message if not already sent
            if not session.state.greeting_sent:
                logger.info("Sending greeting")
                
                user_name = user_data.name.split()[0] if user_data.name else ""
                greeting_text = f"Hello {user_name}, welcome to Intervux.".strip()
                
                full_text = f"""{greeting_text}

I'll be conducting your interview today.

Before we begin, please upload your resume so I can tailor questions based on your experience."""

                await self._send_avatar_with_audio(
                    ws=ws,
                    text=full_text,
                    question_index=0,
                    total_questions=0,
                )
                session.state.greeting_sent = True

            # Transition to waiting for resume
            session.state.transition_to(InterviewPhase.WAITING_RESUME)

            logger.info(f"Interview session started for user {user_data.user_id}")
            logger.info("Waiting for resume upload")

            # Main message loop
            while True:
                message = await self._recv_with_timeout(ws)
                
                # Handle binary audio data
                if message.get("bytes"):
                    response = await session.handle_message(message)
                    
                    # Handle audio chunks - may return partial transcript
                    if response:
                        await self._send_json(ws, response)
                    continue
                
                # Handle text messages
                text = message.get("text")
                if not text:
                    await self._send_error(
                        ws,
                        "EXPECTED_JSON",
                        "Expected text message with JSON payload.",
                        recoverable=True,
                    )
                    continue
                
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    await self._send_error(
                        ws,
                        "INVALID_JSON",
                        "Invalid JSON payload.",
                        recoverable=True,
                    )
                    continue
                
                # Route to session
                wrapped_message = {"data": data, "text": text}
                response = await session.handle_message(wrapped_message)
                
                if response:
                    # Handle special response types
                    if response.get("type") == "question":
                        # Send question with TTS
                        await self._send_evaluation_response(ws, response)
                        await self._send_question_with_audio(ws, session, response)
                        
                    elif response.get("type") == "next_question":
                        # Handle next question response
                        eval_data = response.get("question", {}).get("data", {})
                        next_q = response.get("next_question", {})
                        
                        await self._send_json(ws, {"type": "evaluation", "data": eval_data})
                        await self._send_question_with_audio(ws, session, next_q)
                        
                    elif response.get("type") == "complete":
                        # Interview complete
                        eval_data = response.get("evaluation", {}).get("data", {})
                        final = response.get("final", {})
                        
                        await self._send_json(ws, {"type": "evaluation", "data": eval_data})
                        await self._send_json(ws, final)
                        
                    elif response.get("type") == "phase":
                        await self._send_json(ws, response)
                        
                    else:
                        await self._send_json(ws, response)

        except WebSocketDisconnect:
            logger.info(
                "WebSocket disconnected",
                extra={"extra_data": {"session_id": session_id}},
            )
        except TimeoutError as exc:
            await self._send_error(
                ws,
                "TIMEOUT",
                str(exc),
                recoverable=False,
            )
            await self._close_ws(ws, code=1001)
        except Exception:
            metrics.record_error()
            logger.exception(
                "WebSocket error",
                extra={"extra_data": {"session_id": session_id}},
            )
            await self._send_error(
                ws,
                "INTERNAL_ERROR",
                "Interview session failed.",
                recoverable=False,
            )
            await self._close_ws(ws, code=1011)
        finally:
            await session.cleanup()
            await self._registry.unregister(session_id)
            self._connections.discard(ws)
            await self._release_session_slot()
            metrics.record_gauge("active_sessions", self._active_sessions)

    async def _send_question_with_audio(
        self,
        ws: WebSocket,
        session: InterviewSession,
        question_data: Dict[str, Any],
    ) -> None:
        """Send question with TTS audio."""
        text = question_data.get("text", "")
        question_index = question_data.get("question_index", 1)
        total_questions = question_data.get("total_questions", 2)
        
        # Send avatar sync
        await self._send_json(
            ws,
            {
                "type": "avatar_sync",
                "text": text,
                "question_index": question_index,
                "total_questions": total_questions,
            },
        )
        
        # Synthesize and send TTS
        audio_chunks = await asyncio.to_thread(self._synthesize_tts_chunks, text)
        
        for chunk in audio_chunks:
            visemes = chunk.get("visemes", [])
            audio_bytes = chunk.get("audio_bytes", b"")
            
            if not audio_bytes:
                continue
                
            await self._send_json(
                ws,
                {"type": "avatar_visemes", "visemes": visemes},
            )
            await self._send_bytes(ws, bytes(audio_bytes))

    async def _send_avatar_with_audio(
        self,
        ws: WebSocket,
        text: str,
        question_index: int,
        total_questions: int,
        preloaded_audio_chunks: list[dict[str, Any]] | None = None,
    ):
        """Send avatar sync with TTS audio."""
        await self._send_json(
            ws,
            {
                "type": "avatar_sync",
                "text": text,
                "question_index": question_index,
                "total_questions": total_questions,
            },
        )

        # Synthesize TTS
        if preloaded_audio_chunks is not None:
            audio_chunks = preloaded_audio_chunks
        else:
            audio_chunks = await asyncio.to_thread(self._synthesize_tts_chunks, text)

        for chunk in audio_chunks:
            visemes = chunk.get("visemes", [])
            audio_bytes = chunk.get("audio_bytes", b"")
            if not isinstance(audio_bytes, (bytes, bytearray)) or not audio_bytes:
                continue

            await self._send_json(
                ws,
                {
                    "type": "avatar_visemes",
                    "visemes": visemes,
                },
            )
            await self._send_bytes(ws, bytes(audio_bytes))

    # ==================== Network Helpers ====================

    async def _recv_with_timeout(self, ws: WebSocket) -> Dict[str, Any]:
        """Receive message with timeout."""
        try:
            message = await asyncio.wait_for(
                ws.receive(), 
                timeout=self.receive_timeout_s
            )
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out waiting for client message") from exc

        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect(message.get("code", 1001))
        return message

    async def _send_json(self, ws: WebSocket, payload: Dict[str, Any]) -> None:
        """Send JSON message."""
        try:
            await asyncio.wait_for(
                ws.send_json(payload), 
                timeout=self.send_timeout_s
            )
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending JSON response") from exc

    async def _send_bytes(self, ws: WebSocket, data: bytes) -> None:
        """Send binary data."""
        try:
            await asyncio.wait_for(
                ws.send_bytes(data), 
                timeout=self.send_timeout_s
            )
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending binary data") from exc

    async def _send_error(
        self,
        ws: WebSocket,
        code: str,
        message: str,
        recoverable: bool,
    ) -> None:
        """Send error message."""
        metrics.record_error()
        await self._send_json(
            ws,
            {
                "type": "error",
                "code": code,
                "message": message,
                "recoverable": recoverable,
            },
        )

    async def _close_ws(self, ws: WebSocket, code: int) -> None:
        """Close WebSocket."""
        try:
            await ws.close(code=code)
        except Exception:
            logger.debug("WebSocket close failed", exc_info=True)

    # ==================== Session Management ====================

    async def _try_acquire_session_slot(self) -> bool:
        """Try to acquire a session slot."""
        async with self._session_lock:
            if self._active_sessions >= self.max_concurrent_sessions:
                return False
            self._active_sessions += 1
            metrics.record_gauge("active_sessions", self._active_sessions)
            return True

    async def _release_session_slot(self) -> None:
        """Release session slot."""
        async with self._session_lock:
            if self._active_sessions > 0:
                self._active_sessions -= 1
            metrics.record_gauge("active_sessions", self._active_sessions)

    async def _mark_pending(self, delta: int) -> None:
        """Mark pending connection."""
        async with self._session_lock:
            self._pending_connections = max(0, self._pending_connections + delta)
            metrics.record_gauge("queue_depth", self._pending_connections)

    async def _allow_ip(self, ip: str) -> bool:
        """Check if IP is allowed (rate limiting)."""
        now = time.time()
        window_start = now - 60.0

        async with self._rate_limit_lock:
            hits = self._ip_hits.get(ip, [])
            hits = [ts for ts in hits if ts >= window_start]
            if len(hits) >= self.rate_limit_per_minute:
                self._ip_hits[ip] = hits
                return False

            hits.append(now)
            self._ip_hits[ip] = hits
            return True

    def _build_load_policy(self) -> Dict[str, Any]:
        """Build session load policy based on current load."""
        if self.max_concurrent_sessions <= 0:
            load_ratio = 1.0
        else:
            load_ratio = self._active_sessions / float(self.max_concurrent_sessions)
            
        answer_cycle_p95 = metrics.latency_percentile("answer_cycle_total", 0.95, 0.0)
        adaptive_high_latency = answer_cycle_p95 > 6.0

        question_count = self.total_questions
        question_temperature = 0.7
        evaluation_temperature = 0.1
        lightweight_eval = False

        if load_ratio >= 0.8:
            question_count = max(1, self.total_questions - 1)
            question_temperature = 0.35
            evaluation_temperature = 0.08
            lightweight_eval = True
        elif load_ratio >= 0.6:
            question_temperature = 0.5
            evaluation_temperature = 0.1

        if adaptive_high_latency:
            question_count = max(1, min(question_count, 2) - 1)
            question_temperature = min(question_temperature, 0.45)
            evaluation_temperature = min(evaluation_temperature, 0.08)
            lightweight_eval = True

        return {
            "load_ratio": round(load_ratio, 3),
            "answer_cycle_p95_s": round(answer_cycle_p95, 3),
            "adaptive_high_latency": adaptive_high_latency,
            "question_count": question_count,
            "question_temperature": question_temperature,
            "evaluation_temperature": evaluation_temperature,
            "lightweight_eval": lightweight_eval,
        }

    @staticmethod
    def _client_ip(ws: WebSocket) -> str:
        """Get client IP from WebSocket."""
        if ws.client and ws.client.host:
            return ws.client.host
        return "unknown"

    def _synthesize_tts_chunks(self, text: str) -> list:
        """Split text and synthesize TTS."""
        import re
        chunks = []

        for segment in self._split_sentences(text):
            audio_bytes, visemes = synthesize_speech_with_visemes(segment)
            if not visemes:
                duration_ms = self._wav_duration_ms(audio_bytes)
                visemes = viseme_service.generate_timeline(duration_ms)

            chunks.append({
                "text": segment,
                "audio_bytes": audio_bytes,
                "visemes": visemes,
            })

        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list:
        """Split text into sentences."""
        clean = (text or "").strip()
        if not clean:
            return []

        parts = re.split(r"(?<=[.!?])\s+", clean)
        segments = [part.strip() for part in parts if part.strip()]
        return segments or [clean]

    @staticmethod
    def _wav_duration_ms(audio_bytes: bytes) -> int:
        """Get WAV duration in milliseconds."""
        import wave
        import io
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                frames = wav_file.getnframes()
                frame_rate = wav_file.getframerate() or 1
                duration_ms = int((frames / frame_rate) * 1000)
                return max(duration_ms, 0)
        except Exception:
            logger.debug("Failed to read WAV duration", exc_info=True)
            return 0

    async def shutdown(self) -> None:
        """Shutdown gateway and cleanup sessions."""
        # Close all connections
        connections = list(self._connections)
        for ws in connections:
            try:
                await self._send_json(
                    ws,
                    {
                        "type": "server_shutdown",
                        "message": "Server is shutting down. Please reconnect.",
                        "recoverable": True,
                    },
                )
            except Exception:
                logger.debug("Failed to send shutdown message to websocket", exc_info=True)
            await self._close_ws(ws, code=1001)
        
        # Cleanup all sessions
        await self._registry.cleanup_all()

    def runtime_stats(self) -> Dict[str, int]:
        """Return runtime counters for monitor gauges."""
        return {
            "active_sessions": self._active_sessions,
            "queue_depth": self._pending_connections,
            "max_concurrent_sessions": self.max_concurrent_sessions,
        }


# Need re for sentence splitting
import re

