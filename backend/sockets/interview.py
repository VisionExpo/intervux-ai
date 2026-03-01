import asyncio
import json
import os
import time
import uuid
from functools import partial
from typing import Any, Dict, Set

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from backend.core.agent_ocr import parse_resume_bytes
from backend.core.llm_brain import (
    evaluate_answer,
    generate_final_report,
    generate_questions,
)
from backend.models.interview import InterviewState, ResumeData
from backend.services.stt_service import transcribe_audio_bytes
from backend.services.tts_service import synthesize_speech
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)


class InterviewSocket:
    """
    One WebSocket connection maps to one isolated interview session.
    """

    def __init__(self, total_questions: int = 2):
        self.total_questions = total_questions
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        self.receive_timeout_s = int(os.getenv("WS_RECEIVE_TIMEOUT_S", "120"))
        self.send_timeout_s = int(os.getenv("WS_SEND_TIMEOUT_S", "20"))
        self.max_audio_bytes = int(os.getenv("WS_MAX_AUDIO_BYTES", "20000000"))
        self.max_resume_b64_chars = int(
            os.getenv("WS_MAX_RESUME_B64_CHARS", "14000000")
        )
        self._session_lock = asyncio.Lock()
        self._active_sessions = 0
        self._connections: Set[WebSocket] = set()

    async def handle(self, ws: WebSocket):
        await ws.accept()
        if not await self._try_acquire_session_slot():
            await self._safe_send_json(
                ws,
                {
                    "type": "error",
                    "code": "SERVER_OVERLOADED",
                    "message": "Server is at capacity. Try again shortly.",
                    "recoverable": False,
                },
            )
            await self._close_ws(ws, code=1013)
            return

        session_id = str(uuid.uuid4())
        state = InterviewState()
        self._connections.add(ws)

        logger.info(
            "WebSocket session started",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "active_sessions": self._active_sessions,
                }
            },
        )

        try:
            await self._send_avatar_with_audio(
                ws=ws,
                text="Welcome to Intervux AI. Please upload your resume.",
                question_index=0,
                total_questions=0,
            )

            resume_payload = await self._wait_for_resume_upload(ws)
            await self._bootstrap_interview(
                ws=ws,
                state=state,
                resume_payload=resume_payload,
                session_id=session_id,
            )

            while state.current_index < len(state.questions):
                answer_audio = await self._wait_for_audio_answer(ws)
                await self._process_answer(
                    ws=ws,
                    state=state,
                    answer_audio=answer_audio,
                    session_id=session_id,
                )

            await self._complete_interview(ws=ws, state=state, session_id=session_id)
            await self._close_ws(ws, code=1000)
            logger.info(
                "WebSocket session completed",
                extra={"extra_data": {"session_id": session_id}},
            )
        except WebSocketDisconnect:
            logger.info(
                "WebSocket session disconnected",
                extra={"extra_data": {"session_id": session_id}},
            )
        except TimeoutError as exc:
            await self._send_error(
                ws=ws,
                code="TIMEOUT",
                message=str(exc),
                recoverable=False,
            )
            await self._close_ws(ws, code=1001)
        except ValueError as exc:
            await self._send_error(
                ws=ws,
                code="BAD_PAYLOAD",
                message=str(exc),
                recoverable=True,
            )
            await self._close_ws(ws, code=1003)
        except Exception:
            metrics.record_error()
            logger.exception(
                "WebSocket interview failed",
                extra={"extra_data": {"session_id": session_id}},
            )
            await self._send_error(
                ws=ws,
                code="INTERNAL_ERROR",
                message="Interview session failed.",
                recoverable=False,
            )
            await self._close_ws(ws, code=1011)
        finally:
            state.reset()
            self._connections.discard(ws)
            await self._release_session_slot()

    async def _recv_with_timeout(self, ws: WebSocket) -> Dict[str, Any]:
        try:
            message = await asyncio.wait_for(ws.receive(), timeout=self.receive_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out waiting for client message") from exc

        if message.get("type") == "websocket.disconnect":
            raise WebSocketDisconnect(message.get("code", 1001))
        return message

    async def _wait_for_resume_upload(self, ws: WebSocket) -> Dict[str, str]:
        while True:
            message = await self._recv_with_timeout(ws)
            payload = message.get("text")
            if not payload:
                await self._send_error(
                    ws=ws,
                    code="EXPECTED_JSON",
                    message="Expected resume_upload JSON message.",
                    recoverable=True,
                )
                continue

            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                await self._send_error(
                    ws=ws,
                    code="INVALID_JSON",
                    message="Invalid JSON payload.",
                    recoverable=True,
                )
                continue

            msg_type = data.get("type")
            if msg_type == "ping":
                await self._safe_send_json(ws, {"type": "pong"})
                continue

            if msg_type != "resume_upload":
                await self._send_error(
                    ws=ws,
                    code="UNEXPECTED_MESSAGE",
                    message="Expected type=resume_upload.",
                    recoverable=True,
                )
                continue

            file_name = data.get("file_name")
            file_bytes = data.get("file_bytes")

            if not isinstance(file_name, str) or not file_name.strip():
                raise ValueError("resume_upload.file_name must be a non-empty string")
            if not isinstance(file_bytes, str) or not file_bytes.strip():
                raise ValueError("resume_upload.file_bytes must be a non-empty string")
            if len(file_bytes) > self.max_resume_b64_chars:
                raise ValueError("resume_upload file is too large")

            return {"file_name": file_name.strip(), "file_bytes": file_bytes}

    async def _bootstrap_interview(
        self,
        ws: WebSocket,
        state: InterviewState,
        resume_payload: Dict[str, str],
        session_id: str,
    ):
        resume_start = time.time()
        _, extracted = await asyncio.to_thread(
            partial(
                parse_resume_bytes,
                file_name=resume_payload["file_name"],
                file_bytes_b64=resume_payload["file_bytes"],
            )
        )
        try:
            state.profile = ResumeData(**extracted)
        except ValidationError:
            state.profile = ResumeData()
        metrics.record_latency("resume_parsing", time.time() - resume_start)
        metrics.record_latency("phase_resume_parse", time.time() - resume_start)

        question_start = time.time()
        state.questions = await asyncio.to_thread(
            partial(
                generate_questions,
                profile=state.profile.model_dump(),
                num_questions=self.total_questions,
            )
        )
        state.current_index = 0
        metrics.record_latency("question_generation", time.time() - question_start)
        metrics.record_latency(
            "phase_question_generation", time.time() - question_start
        )

        if not state.questions:
            raise RuntimeError("Question generation returned no questions")

        logger.info(
            "Interview initialized",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "skills_count": len(state.profile.skills),
                    "questions_count": len(state.questions),
                }
            },
        )

        await self._send_current_question(ws=ws, state=state)

    async def _wait_for_audio_answer(self, ws: WebSocket) -> bytes:
        while True:
            message = await self._recv_with_timeout(ws)
            answer_audio = message.get("bytes")
            if answer_audio:
                if len(answer_audio) > self.max_audio_bytes:
                    raise ValueError("Audio payload too large")
                return answer_audio

            payload = message.get("text")
            if payload:
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    await self._send_error(
                        ws=ws,
                        code="INVALID_JSON",
                        message="Invalid JSON payload.",
                        recoverable=True,
                    )
                    continue

                msg_type = data.get("type")
                if msg_type == "ping":
                    await self._safe_send_json(ws, {"type": "pong"})
                    continue

                await self._send_error(
                    ws=ws,
                    code="UNEXPECTED_MESSAGE",
                    message="Expected binary audio answer.",
                    recoverable=True,
                )
                continue

            await self._send_error(
                ws=ws,
                code="UNSUPPORTED_FRAME",
                message="Unsupported frame type.",
                recoverable=True,
            )

    async def _process_answer(
        self,
        ws: WebSocket,
        state: InterviewState,
        answer_audio: bytes,
        session_id: str,
    ):
        answer_cycle_start = time.time()
        question = state.questions[state.current_index]

        stt_start = time.time()
        transcript = await asyncio.to_thread(
            partial(
                transcribe_audio_bytes,
                audio_bytes=answer_audio,
                suffix=self._detect_audio_suffix(answer_audio),
            )
        )
        metrics.record_latency("stt", time.time() - stt_start)
        metrics.record_latency("phase_stt", time.time() - stt_start)
        if not transcript:
            transcript = "(No transcript captured)"

        eval_start = time.time()
        evaluation = await asyncio.to_thread(
            partial(
                evaluate_answer,
                question=question,
                answer=transcript,
                profile=state.profile.model_dump(),
            )
        )
        metrics.record_latency("evaluation", time.time() - eval_start)
        metrics.record_latency("phase_evaluation", time.time() - eval_start)

        state.answers.append(
            {
                "question": question,
                "answer": transcript,
                "evaluation": evaluation,
            }
        )

        await self._safe_send_json(
            ws,
            {
                "type": "evaluation",
                "data": {
                    "question_index": state.current_index + 1,
                    "question": question,
                    "transcript": transcript,
                    "evaluation": evaluation,
                },
            },
        )

        state.current_index += 1
        logger.info(
            "Answer evaluated",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "question_index": state.current_index,
                    "transcript_length": len(transcript),
                }
            },
        )

        if state.current_index < len(state.questions):
            await self._send_current_question(ws=ws, state=state)

        metrics.record_latency("answer_cycle_total", time.time() - answer_cycle_start)

    async def _complete_interview(
        self, ws: WebSocket, state: InterviewState, session_id: str
    ):
        report_start = time.time()
        report = await asyncio.to_thread(
            partial(
                generate_final_report,
                profile=state.profile.model_dump(),
                answers=state.answers,
            )
        )
        metrics.record_latency("final_report", time.time() - report_start)
        metrics.record_interview_completed()
        state.final_report = report

        await self._safe_send_json(ws, {"type": "interview_complete", "report": report})
        logger.info(
            "Interview completed",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "answers_count": len(state.answers),
                }
            },
        )

    async def _send_current_question(self, ws: WebSocket, state: InterviewState):
        question_text = state.questions[state.current_index]
        await self._send_avatar_with_audio(
            ws=ws,
            text=question_text,
            question_index=state.current_index + 1,
            total_questions=len(state.questions),
        )

    async def _send_avatar_with_audio(
        self, ws: WebSocket, text: str, question_index: int, total_questions: int
    ):
        await self._safe_send_json(
            ws,
            {
                "type": "avatar_sync",
                "text": text,
                "question_index": question_index,
                "total_questions": total_questions,
            },
        )

        tts_start = time.time()
        audio_bytes = await asyncio.to_thread(self._synthesize_wav_bytes, text)
        metrics.record_latency("tts", time.time() - tts_start)
        await self._safe_send_bytes(ws, audio_bytes)

    async def _safe_send_json(self, ws: WebSocket, payload: Dict[str, Any]):
        try:
            await asyncio.wait_for(ws.send_json(payload), timeout=self.send_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending JSON response") from exc

    async def _safe_send_bytes(self, ws: WebSocket, data: bytes):
        try:
            await asyncio.wait_for(ws.send_bytes(data), timeout=self.send_timeout_s)
        except asyncio.TimeoutError as exc:
            raise TimeoutError("Timed out sending binary audio") from exc

    async def _send_error(
        self, ws: WebSocket, code: str, message: str, recoverable: bool
    ):
        metrics.record_error()
        await self._safe_send_json(
            ws,
            {
                "type": "error",
                "code": code,
                "message": message,
                "recoverable": recoverable,
            },
        )

    async def _close_ws(self, ws: WebSocket, code: int):
        try:
            await ws.close(code=code)
        except Exception:
            pass

    async def _try_acquire_session_slot(self) -> bool:
        async with self._session_lock:
            if self._active_sessions >= self.max_concurrent_sessions:
                return False
            self._active_sessions += 1
            return True

    async def _release_session_slot(self):
        async with self._session_lock:
            if self._active_sessions > 0:
                self._active_sessions -= 1

    async def shutdown(self):
        connections = list(self._connections)
        for ws in connections:
            try:
                await self._safe_send_json(
                    ws,
                    {
                        "type": "server_shutdown",
                        "message": "Server is shutting down. Please reconnect.",
                        "recoverable": True,
                    },
                )
            except Exception:
                pass
            await self._close_ws(ws, code=1001)

    @staticmethod
    def _synthesize_wav_bytes(text: str) -> bytes:
        audio_url = synthesize_speech(text)
        relative_path = audio_url.lstrip("/")
        if os.path.exists("/app"):
            file_path = os.path.join("/app", relative_path.replace("/", os.sep))
        else:
            file_path = os.path.join("backend", relative_path.replace("/", os.sep))
        try:
            with open(file_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    @staticmethod
    def _detect_audio_suffix(audio_bytes: bytes) -> str:
        if audio_bytes.startswith(b"RIFF"):
            return ".wav"
        if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            return ".webm"
        if audio_bytes.startswith(b"ID3"):
            return ".mp3"
        return ".wav"
