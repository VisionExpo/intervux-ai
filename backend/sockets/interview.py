import json
import os
import time
import uuid
from typing import Any, Dict

from fastapi import WebSocket, WebSocketDisconnect

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

    async def handle(self, ws: WebSocket):
        await ws.accept()
        session_id = str(uuid.uuid4())
        state = InterviewState()

        logger.info(
            "WebSocket session started",
            extra={"extra_data": {"session_id": session_id}},
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
        except WebSocketDisconnect:
            logger.info(
                "WebSocket session disconnected",
                extra={"extra_data": {"session_id": session_id}},
            )
        except Exception:
            metrics.record_error()
            logger.exception(
                "WebSocket interview failed",
                extra={"extra_data": {"session_id": session_id}},
            )
            await ws.send_json(
                {
                    "type": "error",
                    "message": "Interview session failed.",
                }
            )
            await ws.close(code=1011)
        else:
            await ws.close(code=1000)
            logger.info(
                "WebSocket session completed",
                extra={"extra_data": {"session_id": session_id}},
            )

    async def _wait_for_resume_upload(self, ws: WebSocket) -> Dict[str, Any]:
        while True:
            message = await ws.receive()
            payload = message.get("text")
            if not payload:
                await ws.send_json(
                    {"type": "error", "message": "Expected resume_upload JSON."}
                )
                continue

            data = json.loads(payload)
            if data.get("type") != "resume_upload":
                await ws.send_json(
                    {"type": "error", "message": "Expected type=resume_upload."}
                )
                continue

            if not data.get("file_bytes"):
                await ws.send_json(
                    {"type": "error", "message": "resume_upload missing file_bytes."}
                )
                continue

            return data

    async def _bootstrap_interview(
        self,
        ws: WebSocket,
        state: InterviewState,
        resume_payload: Dict[str, Any],
        session_id: str,
    ):
        resume_start = time.time()
        _, extracted = parse_resume_bytes(
            file_name=resume_payload.get("file_name", "resume.pdf"),
            file_bytes_b64=resume_payload["file_bytes"],
        )
        state.profile = ResumeData(**extracted)
        metrics.record_latency("resume_parsing", time.time() - resume_start)

        question_start = time.time()
        state.questions = generate_questions(
            profile=state.profile.model_dump(),
            num_questions=self.total_questions,
        )
        state.current_index = 0
        metrics.record_latency("question_generation", time.time() - question_start)

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
            message = await ws.receive()
            answer_audio = message.get("bytes")
            if answer_audio:
                return answer_audio

            payload = message.get("text")
            if payload:
                try:
                    data = json.loads(payload)
                except Exception:
                    data = {}

                if data.get("type") == "resume_upload":
                    await ws.send_json(
                        {
                            "type": "error",
                            "message": "Resume already uploaded for this session.",
                        }
                    )
                    continue

            await ws.send_json({"type": "error", "message": "Expected audio bytes."})

    async def _process_answer(
        self,
        ws: WebSocket,
        state: InterviewState,
        answer_audio: bytes,
        session_id: str,
    ):
        question = state.questions[state.current_index]

        stt_start = time.time()
        transcript = transcribe_audio_bytes(
            audio_bytes=answer_audio,
            suffix=self._detect_audio_suffix(answer_audio),
        )
        metrics.record_latency("stt", time.time() - stt_start)

        eval_start = time.time()
        evaluation = evaluate_answer(
            question=question,
            answer=transcript,
            profile=state.profile.model_dump(),
        )
        metrics.record_latency("evaluation", time.time() - eval_start)

        state.answers.append(
            {
                "question": question,
                "answer": transcript,
                "evaluation": evaluation,
            }
        )

        await ws.send_json(
            {
                "type": "evaluation",
                "data": {
                    "question_index": state.current_index + 1,
                    "question": question,
                    "transcript": transcript,
                    "evaluation": evaluation,
                },
            }
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

    async def _complete_interview(
        self, ws: WebSocket, state: InterviewState, session_id: str
    ):
        report_start = time.time()
        report = generate_final_report(
            profile=state.profile.model_dump(),
            answers=state.answers,
        )
        metrics.record_latency("final_report", time.time() - report_start)
        metrics.record_interview_completed()

        state.final_report = report

        await ws.send_json({"type": "interview_complete", "report": report})

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
        await ws.send_json(
            {
                "type": "avatar_sync",
                "text": text,
                "question_index": question_index,
                "total_questions": total_questions,
            }
        )

        tts_start = time.time()
        audio_bytes = self._synthesize_wav_bytes(text)
        metrics.record_latency("tts", time.time() - tts_start)
        await ws.send_bytes(audio_bytes)

    @staticmethod
    def _synthesize_wav_bytes(text: str) -> bytes:
        audio_url = synthesize_speech(text)
        relative_path = audio_url.lstrip("/")
        if os.path.exists("/app"):
            file_path = os.path.join("/app", relative_path.replace("/", os.sep))
        else:
            file_path = os.path.join("backend", relative_path.replace("/", os.sep))
        with open(file_path, "rb") as f:
            return f.read()

    @staticmethod
    def _detect_audio_suffix(audio_bytes: bytes) -> str:
        if audio_bytes.startswith(b"RIFF"):
            return ".wav"
        if audio_bytes.startswith(b"\x1a\x45\xdf\xa3"):
            return ".webm"
        if audio_bytes.startswith(b"ID3"):
            return ".mp3"
        return ".wav"
