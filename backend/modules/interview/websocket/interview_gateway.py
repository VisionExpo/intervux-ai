import asyncio
import json
import os
import re
import time
import uuid
import wave
import io
import redis.asyncio as aioredis
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from backend.core.security.jwt_service import TokenData, verify_token
from backend.models.interview import InterviewPhase
from backend.modules.interview.sessions.interview_session import InterviewSession
from backend.modules.interview.sessions.registry import get_session_registry
from backend.services.tts_service import synthesize_speech_with_visemes
from backend.services.viseme_service import VisemeService
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)
viseme_service = VisemeService()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class InterviewGateway:
    def __init__(self, total_questions: int = 2):
        self.total_questions = total_questions
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_WS_PER_MINUTE", "30"))
        self.receive_timeout_s = int(os.getenv("WS_RECEIVE_TIMEOUT_S", "120"))
        self.send_timeout_s = int(os.getenv("WS_SEND_TIMEOUT_S", "20"))
        
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        self._registry = get_session_registry()
        
        # Local tracker for clean shutdown
        self._connections: Set[WebSocket] = set()
        self._active_celery_tasks: Dict[str, Set[Any]] = {}

    async def _ping_loop(self, ws: WebSocket, session_id: str):
        """Keep LoadBalancers happy with 20s pings."""
        try:
            while True:
                await asyncio.sleep(20)
                if ws.client_state.name == "CONNECTED":
                    await self._send_json(ws, {"type": "ping", "message": "heartbeat"})
                else:
                    break
        except Exception:
            pass

    async def _pubsub_listener(self, ws: WebSocket, session_id: str, session: InterviewSession):
        """Listen for transcription results pushed by Celery over Redis and forward to UI."""
        from backend.services.redis_manager import redis_client
        try:
            async for message in redis_client.subscribe(f"interview:results:{session_id}"):
                if message.get("type") == "partial_transcript":
                    text = message.get("text", "")
                    if text:
                        session._partial_transcript = text
                        session._partial_count += 1
                        metrics.increment_counter("partial_transcript_count")
                        await self._send_json(ws, {"type": "partial_transcript", "text": text})
        except Exception as e:
            logger.warning(f"PubSub listener closed for {session_id}: {e}")

    async def _allow_ip(self, ip: str) -> bool:
        """Redis token bucket / sliding window rate limiter."""
        key = f"rl:ws:{ip}"
        now = int(time.time())
        window_start = now - 60

        try:
            pipeline = self.redis.pipeline()
            pipeline.zremrangebyscore(key, 0, window_start)
            pipeline.zcard(key)
            pipeline.zadd(key, {str(now): now})
            pipeline.expire(key, 60)

            # Keep auth handshake responsive even when Redis is down/unreachable.
            results = await asyncio.wait_for(pipeline.execute(), timeout=1.0)
            req_count = results[1]
            return req_count < self.rate_limit_per_minute
        except Exception:
            logger.warning("WS rate limiter unavailable; allowing connection")
            return True

    async def handle(self, ws: WebSocket) -> None:
        token = ws.query_params.get("token")
        if not token:
            await ws.accept()
            await self._send_error(ws, "UNAUTHORIZED", "Missing authentication token", recoverable=True)
            await self._close_ws(ws, code=1008)
            return

        try:
            user_data: TokenData = await verify_token(token)
        except Exception:
            await ws.accept()
            await self._send_error(ws, "UNAUTHORIZED", "Invalid authentication token", recoverable=True)
            await self._close_ws(ws, code=1008)
            return

        mock_interview_session_id = ws.query_params.get("mock_session_id")

        client_ip = self._client_ip(ws)
        if not await self._allow_ip(client_ip):
            await ws.accept()
            await self._send_error(ws, "RATE_LIMITED", "Too many connection attempts from this IP.", recoverable=True)
            await self._close_ws(ws, code=1008)
            metrics.increment_counter("rate_limit_rejections")
            return

        await ws.accept()
        
        active_sessions = await self._registry.count()
        if active_sessions >= self.max_concurrent_sessions:
            await self._send_error(ws, "SERVER_OVERLOADED", "Server is at capacity. Try again shortly.", recoverable=False)
            await self._close_ws(ws, code=1013)
            return

        session_id = str(uuid.uuid4())
        session_policy = self._build_load_policy(active_sessions)

        session = InterviewSession(
            session_id=session_id,
            user_id=user_data.user_id,
            session_policy=session_policy,
            mock_interview_session_id=mock_interview_session_id,
        )

        metadata = {
            "user_id": user_data.user_id,
            "mock_id": mock_interview_session_id,
            "created_at": time.time()
        }
        await self._registry.register(session_id, metadata)
        self._connections.add(ws)
        self._active_celery_tasks[session_id] = set()
        
        ping_task = asyncio.create_task(self._ping_loop(ws, session_id))
        pubsub_task = asyncio.create_task(self._pubsub_listener(ws, session_id, session))

        try:
            if not session.state.greeting_sent:
                user_name = user_data.name.split()[0] if user_data.name else ""
                greeting_text = f"Hello {user_name}, welcome to Intervux.".strip()
                full_text = (
                    f"{greeting_text}\n\n"
                    "I'll be conducting your interview today.\n\n"
                    "Before we begin, please upload your resume so I can tailor "
                    "questions based on your experience."
                )
                # Send greeting synchronously to prevent AnyIO stream lockups in TestClient
                await self._send_avatar_with_audio(ws, session, full_text, 0, 0)
                session.state.greeting_sent = True

            session.state.transition_to(InterviewPhase.WAITING_RESUME)

            while True:
                message = await self._recv_with_timeout(ws)

                if message.get("bytes"):
                    response = await session.handle_message(message)
                    if response:
                        await self._send_json(ws, response)
                        if response.get("type") == "error" and not response.get("recoverable", True):
                            await self._close_ws(ws, code=1011)
                            return
                    continue

                text = message.get("text")
                if not text:
                    await self._send_error(ws, "EXPECTED_JSON", "Expected text message with JSON payload.", recoverable=True)
                    continue

                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    await self._send_error(ws, "INVALID_JSON", "Invalid JSON payload.", recoverable=True)
                    continue

                wrapped_message = {"data": data, "text": text}
                response = await session.handle_message(wrapped_message)

                if response:
                    if response.get("type") == "question":
                        await self._send_evaluation_response(ws, response)
                        await self._send_question_with_audio(ws, session, response)
                    elif response.get("type") == "next_question":
                        eval_data = response.get("question", {}).get("data", {})
                        next_q = response.get("next_question", {})
                        await self._send_json(ws, {"type": "evaluation", "data": eval_data})
                        await self._send_question_with_audio(ws, session, next_q)
                    elif response.get("type") == "complete":
                        eval_data = response.get("evaluation", {}).get("data", {})
                        final = response.get("final", {})
                        await self._send_json(ws, {"type": "evaluation", "data": eval_data})
                        await self._send_json(ws, final)
                    else:
                        await self._send_json(ws, response)
                        if response.get("type") == "error" and not response.get("recoverable", True):
                            await self._close_ws(ws, code=1011)
                            return

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected", extra={"extra_data": {"session_id": session_id}})
        except TimeoutError as exc:
            await self._send_error(ws, "TIMEOUT", str(exc), recoverable=False)
            await self._close_ws(ws, code=1001)
        except Exception:
            metrics.record_error()
            await self._send_error(ws, "INTERNAL_ERROR", "Interview session failed.", recoverable=False)
            await self._close_ws(ws, code=1011)
        finally:
            ping_task.cancel()
            pubsub_task.cancel()
            
            # Revoke any lingering Celery TTS tasks for this session
            pending_tts = self._active_celery_tasks.pop(session_id, set())
            for tts_task in pending_tts:
                try:
                    if not tts_task.ready():
                        tts_task.revoke(terminate=True)
                except Exception:
                    pass
                    
            await session.cleanup()
            await self._registry.unregister(session_id)
            self._connections.discard(ws)

            # Clean up the PubSub results channel key from Redis
            try:
                await self.redis.delete(f"interview:results:{session_id}")
            except Exception:
                pass

    # Audio Helpers
    async def _send_question_with_audio(self, ws: WebSocket, session: InterviewSession, question_data: Dict[str, Any]) -> None:
        text = question_data.get("text", "")
        question_index = question_data.get("question_index", 1)
        total_questions = question_data.get("total_questions", 2)
        await self._send_json(ws, {"type": "avatar_sync", "text": text, "question_index": question_index, "total_questions": total_questions})
        audio_chunks = await self._synthesize_tts_chunks(session.session_id, text)
        for chunk in audio_chunks:
            visemes = chunk.get("visemes", [])
            audio_bytes = chunk.get("audio_bytes", b"")
            if not audio_bytes:
                continue
            await self._send_json(ws, {"type": "avatar_visemes", "visemes": visemes})
            await self._send_bytes(ws, bytes(audio_bytes))
        await self._send_json(ws, {"type": "phase", "value": "LISTENING"})

    async def _send_avatar_with_audio(self, ws: WebSocket, session: InterviewSession, text: str, question_index: int, total_questions: int) -> None:
        await self._send_json(ws, {"type": "avatar_sync", "text": text, "question_index": question_index, "total_questions": total_questions})
        audio_chunks = await self._synthesize_tts_chunks(session.session_id, text)
        for chunk in audio_chunks:
            visemes = chunk.get("visemes", [])
            audio_bytes = chunk.get("audio_bytes", b"")
            if not audio_bytes:
                continue
            await self._send_json(ws, {"type": "avatar_visemes", "visemes": visemes})
            await self._send_bytes(ws, bytes(audio_bytes))
        if question_index > 0:
            await self._send_json(ws, {"type": "phase", "value": "LISTENING"})

    async def _send_evaluation_response(self, ws: WebSocket, response: Dict[str, Any]) -> None:
        eval_payload = response.get("data")
        if isinstance(eval_payload, dict):
            await self._send_json(ws, {"type": "evaluation", "data": eval_payload})

    # Network helpers
    async def _recv_with_timeout(self, ws: WebSocket) -> Dict[str, Any]:
        try:
            message = await asyncio.wait_for(ws.receive(), timeout=self.receive_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out waiting for client message") from exc
        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect(message.get("code", 1001))
        return message

    async def _send_json(self, ws: WebSocket, payload: Dict[str, Any]) -> None:
        try:
            await asyncio.wait_for(ws.send_json(payload), timeout=self.send_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending JSON response") from exc

    async def _send_bytes(self, ws: WebSocket, data: bytes) -> None:
        try:
            await asyncio.wait_for(ws.send_bytes(data), timeout=self.send_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending binary data") from exc

    async def _send_error(self, ws: WebSocket, code: str, message: str, recoverable: bool) -> None:
        await self._send_json(ws, {"type": "error", "code": code, "message": message, "recoverable": recoverable})

    async def _close_ws(self, ws: WebSocket, code: int) -> None:
        try:
            await ws.close(code=code)
        except Exception:
            pass

    def _build_load_policy(self, active_sessions: int) -> Dict[str, Any]:
        load_ratio = 1.0 if self.max_concurrent_sessions <= 0 else active_sessions / float(self.max_concurrent_sessions)
        return {
            "load_ratio": round(load_ratio, 3),
            "question_count": self.total_questions,
            "question_temperature": 0.7 if load_ratio < 0.8 else 0.35,
            "evaluation_temperature": 0.1 if load_ratio < 0.8 else 0.08,
            "lightweight_eval": load_ratio >= 0.8,
        }

    async def shutdown(self) -> None:
        if getattr(self, "redis", None):
            await self.redis.close()
        for ws in list(self._connections):
            await self._close_ws(ws, 1001)
        self._connections.clear()

    def runtime_stats(self) -> Dict[str, Any]:
        return {
            "active_sessions": len(self._connections),
            "queue_depth": 0,
            "max_concurrent_sessions": self.max_concurrent_sessions,
        }

    @staticmethod
    def _client_ip(ws: WebSocket) -> str:
        return ws.client.host if ws.client and ws.client.host else "unknown"

    async def _synthesize_tts_chunks(self, session_id: str, text: str) -> list:
        if os.getenv("DISABLE_TTS", "false").lower() == "true":
            return []

        from backend.core.celery_tasks import synthesize_tts_task
        import base64

        segments = self._split_sentences(text)

        # Fire all Celery TTS tasks in parallel
        celery_tasks = [synthesize_tts_task.delay(seg) for seg in segments]
        
        # Track these tasks for the session
        session_task_set = self._active_celery_tasks.get(session_id)
        if session_task_set is not None:
            for task in celery_tasks:
                session_task_set.add(task)

        chunks = []
        for seg, task in zip(segments, celery_tasks):
            # Await each task result with a timeout so a slow/dead worker
            # doesn't hang the entire WebSocket session.
            deadline = asyncio.get_event_loop().time() + 15.0  # 15 s per segment
            while not task.ready():
                if task.failed():
                    logger.error(f"TTS task failed for segment: {seg[:40]!r}")
                    break
                if asyncio.get_event_loop().time() > deadline:
                    logger.warning(f"TTS task timed out for segment: {seg[:40]!r}")
                    break
                await asyncio.sleep(0.05)

            result = task.result if task.ready() and not task.failed() else None
            
            # Remove from tracking as it's completed/failed/timeout
            if session_task_set is not None:
                session_task_set.discard(task)
                
            if result:
                b64_audio = result.get("audio_b64", "")
                audio_bytes = base64.b64decode(b64_audio) if b64_audio else b""
                visemes = result.get("visemes", [])
                if audio_bytes:
                    chunks.append({"text": seg, "audio_bytes": audio_bytes, "visemes": visemes})
        return chunks

    @staticmethod
    def _split_sentences(text: str) -> list:
        clean = (text or "").strip()
        parts = re.split(r"(?<=[.!?])\s+", clean)
        segments = [part.strip() for part in parts if part.strip()]
        return segments or [clean]

    @staticmethod
    def _wav_duration_ms(audio_bytes: bytes) -> int:
        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                frames = wav_file.getnframes()
                frame_rate = wav_file.getframerate() or 1
                return max(int((frames / frame_rate) * 1000), 0)
        except Exception:
            return 0
