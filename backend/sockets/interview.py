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
    prepare_evaluation_context,
)
from backend.models.interview import InterviewState, ResumeData
from backend.services.stt_service import transcribe_audio_bytes
from backend.services.tts_service import synthesize_speech
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics
from backend.utils.research_logger import research_logger

logger = get_logger(__name__)


class InterviewSocket:
    """
    One WebSocket connection maps to one isolated interview session.
    """

    def __init__(self, total_questions: int = 2):
        self.total_questions = total_questions
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "5"))
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_WS_PER_MINUTE", "30"))
        self.receive_timeout_s = int(os.getenv("WS_RECEIVE_TIMEOUT_S", "120"))
        self.send_timeout_s = int(os.getenv("WS_SEND_TIMEOUT_S", "20"))
        self.max_audio_bytes = int(os.getenv("WS_MAX_AUDIO_BYTES", "20000000"))
        self.max_resume_b64_chars = int(
            os.getenv("WS_MAX_RESUME_B64_CHARS", "14000000")
        )
        self._session_lock = asyncio.Lock()
        self._rate_limit_lock = asyncio.Lock()
        self._active_sessions = 0
        self._pending_connections = 0
        self._connections: Set[WebSocket] = set()
        self._ip_hits: Dict[str, list[float]] = {}

    async def handle(self, ws: WebSocket):
        client_ip = self._client_ip(ws)

        if not await self._allow_ip(client_ip):
            await ws.accept()
            await self._safe_send_json(
                ws,
                {
                    "type": "error",
                    "code": "RATE_LIMITED",
                    "message": "Too many connection attempts from this IP.",
                    "recoverable": True,
                },
            )
            await self._close_ws(ws, code=1008)
            metrics.increment_counter("rate_limit_rejections")
            return

        await ws.accept()
        await self._mark_pending(delta=1)
        if not await self._try_acquire_session_slot():
            await self._mark_pending(delta=-1)
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
        await self._mark_pending(delta=-1)

        session_id = str(uuid.uuid4())
        state = InterviewState()
        self._connections.add(ws)
        session_policy = self._build_load_policy()
        eval_context_cache: Dict[int, dict] = {}
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
                session_policy=session_policy,
                eval_context_cache=eval_context_cache,
            )

            while state.current_index < len(state.questions):
                answer_audio = await self._wait_for_audio_answer(ws)
                await self._process_answer(
                    ws=ws,
                    state=state,
                    answer_audio=answer_audio,
                    session_id=session_id,
                    session_policy=session_policy,
                    eval_context_cache=eval_context_cache,
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
            metrics.record_gauge("active_sessions", self._active_sessions)

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
        session_policy: Dict[str, Any],
        eval_context_cache: Dict[int, dict],
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
                num_questions=session_policy["question_count"],
                temperature_override=session_policy["question_temperature"],
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

        await self._send_current_question(
            ws=ws,
            state=state,
            profile_dict=state.profile.model_dump(),
            session_policy=session_policy,
            eval_context_cache=eval_context_cache,
        )

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
        session_policy: Dict[str, Any],
        eval_context_cache: Dict[int, dict],
    ):
        answer_cycle_start = time.time()
        current_index = state.current_index
        question = state.questions[state.current_index]

        stt_start = time.time()
        transcript = await asyncio.to_thread(
            partial(
                transcribe_audio_bytes,
                audio_bytes=answer_audio,
                suffix=self._detect_audio_suffix(answer_audio),
            )
        )
        stt_duration = time.time() - stt_start
        metrics.record_latency("stt", stt_duration)
        metrics.record_latency("phase_stt", stt_duration)
        if not transcript:
            transcript = "(No transcript captured)"

        eval_start = time.time()
        prepared_context = eval_context_cache.get(current_index)
        evaluation = await asyncio.to_thread(
            partial(
                evaluate_answer,
                question=question,
                answer=transcript,
                profile=state.profile.model_dump(),
                lightweight=session_policy["lightweight_eval"],
                temperature_override=session_policy["evaluation_temperature"],
                prepared_context=prepared_context,
            )
        )
        eval_duration = time.time() - eval_start
        metrics.record_latency("evaluation", eval_duration)
        metrics.record_latency("phase_evaluation", eval_duration)
        evaluation = self._normalize_scores_for_session(
            evaluation=evaluation,
            previous_answers=state.answers,
        )

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
            await self._send_current_question(
                ws=ws,
                state=state,
                profile_dict=state.profile.model_dump(),
                session_policy=session_policy,
                eval_context_cache=eval_context_cache,
            )

        answer_cycle_duration = time.time() - answer_cycle_start
        metrics.record_latency("answer_cycle_total", answer_cycle_duration)
        self._log_research_record(
            session_id=session_id,
            question_index=current_index + 1,
            transcript=transcript,
            evaluation=evaluation,
            session_policy=session_policy,
            stt_latency=stt_duration,
            eval_latency=eval_duration,
            answer_cycle_latency=answer_cycle_duration,
        )

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

    async def _send_current_question(
        self,
        ws: WebSocket,
        state: InterviewState,
        profile_dict: dict,
        session_policy: Dict[str, Any],
        eval_context_cache: Dict[int, dict],
    ):
        question_text = state.questions[state.current_index]
        preload_task = asyncio.create_task(
            asyncio.to_thread(
                prepare_evaluation_context,
                profile_dict,
                question_text,
                session_policy["lightweight_eval"],
            )
        )

        await self._send_avatar_with_audio(
            ws=ws,
            text=question_text,
            question_index=state.current_index + 1,
            total_questions=len(state.questions),
        )
        try:
            eval_context_cache[state.current_index] = await preload_task
        except Exception:
            metrics.record_error()

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
            metrics.record_gauge("active_sessions", self._active_sessions)
            return True

    async def _release_session_slot(self):
        async with self._session_lock:
            if self._active_sessions > 0:
                self._active_sessions -= 1
            metrics.record_gauge("active_sessions", self._active_sessions)

    async def _mark_pending(self, delta: int):
        async with self._session_lock:
            self._pending_connections = max(0, self._pending_connections + delta)
            metrics.record_gauge("queue_depth", self._pending_connections)

    async def _allow_ip(self, ip: str) -> bool:
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
        if self.max_concurrent_sessions <= 0:
            load_ratio = 1.0
        else:
            load_ratio = self._active_sessions / float(self.max_concurrent_sessions)

        question_count = self.total_questions
        question_temperature = 0.7
        evaluation_temperature = 0.3
        lightweight_eval = False

        if load_ratio >= 0.8:
            question_count = max(1, self.total_questions - 1)
            question_temperature = 0.35
            evaluation_temperature = 0.2
            lightweight_eval = True
        elif load_ratio >= 0.6:
            question_temperature = 0.5
            evaluation_temperature = 0.25

        return {
            "load_ratio": round(load_ratio, 3),
            "question_count": question_count,
            "question_temperature": question_temperature,
            "evaluation_temperature": evaluation_temperature,
            "lightweight_eval": lightweight_eval,
        }

    @staticmethod
    def _client_ip(ws: WebSocket) -> str:
        if ws.client and ws.client.host:
            return ws.client.host
        return "unknown"

    def runtime_stats(self) -> Dict[str, float]:
        return {
            "active_sessions": float(self._active_sessions),
            "queue_depth": float(self._pending_connections),
            "max_concurrent_sessions": float(self.max_concurrent_sessions),
        }

    @staticmethod
    def _normalize_scores_for_session(evaluation: dict, previous_answers: list[dict]) -> dict:
        scores = evaluation.get("scores")
        if not isinstance(scores, dict) or not scores:
            return evaluation

        history_values: Dict[str, list[float]] = {}
        for answer in previous_answers:
            prev_scores = answer.get("evaluation", {}).get("scores", {})
            if not isinstance(prev_scores, dict):
                continue
            for key, value in prev_scores.items():
                try:
                    history_values.setdefault(key, []).append(float(value))
                except Exception:
                    pass

        if not history_values:
            return evaluation

        normalized = dict(scores)
        for key, value in scores.items():
            try:
                raw = float(value)
            except Exception:
                continue

            history = history_values.get(key, [])
            if not history:
                normalized[key] = int(max(0, min(10, round(raw))))
                continue

            avg = sum(history) / len(history)
            target = 7.5
            if avg <= 0:
                factor = 1.0
            else:
                factor = max(0.75, min(1.0, target / avg))
            adjusted = raw * factor
            normalized[key] = int(max(0, min(10, round(adjusted))))

        evaluation["scores"] = normalized
        evaluation.setdefault("meta", {})["normalized"] = True
        return evaluation

    @staticmethod
    def _log_research_record(
        session_id: str,
        question_index: int,
        transcript: str,
        evaluation: dict,
        session_policy: Dict[str, Any],
        stt_latency: float,
        eval_latency: float,
        answer_cycle_latency: float,
    ):
        research_logger.write_evaluation_record(
            {
                "session_id": session_id,
                "question_index": question_index,
                "answer_text": transcript,
                "scores": evaluation.get("scores", {}),
                "confidence_score": evaluation.get("confidence_score"),
                "evaluator_variance": evaluation.get("evaluator_variance"),
                "provider": evaluation.get("meta", {}).get("provider"),
                "load_policy": session_policy,
                "latency": {
                    "stt_s": round(stt_latency, 3),
                    "evaluation_s": round(eval_latency, 3),
                    "answer_cycle_s": round(answer_cycle_latency, 3),
                },
            }
        )

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
