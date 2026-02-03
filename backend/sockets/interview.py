import json
import uuid
from fastapi import WebSocket, WebSocketDisconnect

from backend.core.llm_brain import InterviewerAI
from backend.core.emotion_ai import EmotionAnalyzer
from backend.services.stt_service import STTService
from backend.services.tts_service import TTSService
from backend.services.viseme_service import VisemeService


class InterviewSocket:
    """
    Orchestrates the full real-time interview loop.
    """

    def __init__(self):
        self.llm = InterviewerAI()
        self.stt = STTService()
        self.tts = TTSService()
        self.viseme = VisemeService()
        self.emotion = EmotionAnalyzer()

    async def handle(self, ws: WebSocket):
        session_id = str(uuid.uuid4())
        await ws.accept()

        print(f"[WS] Interview session started: {session_id}")

        # ---- Start Interview Session ----
        resume_stub = {
            "name": "Candidate",
            "skills": ["Python", "DSA"],
            "projects": [],
        }

        opening_text = self.llm.start_session(
            session_id=session_id,
            resume_data=resume_stub,
        )

        # Speak opening
        await self._send_response(ws, opening_text)

        try:
            while True:
                message = await ws.receive()

                # -----------------------
                # AUDIO INPUT (USER)
                # -----------------------
                if "bytes" in message:
                    user_audio = message["bytes"]

                    # STT
                    user_text = self.stt.transcribe(user_audio)
                    if not user_text:
                        continue

                    print(f"[USER] {user_text}")

                    # LLM Response
                    reply_text = self.llm.get_response(
                        session_id, user_text
                    )

                    # Speak + Animate
                    await self._send_response(ws, reply_text)

                # -----------------------
                # JSON EVENTS (FUTURE)
                # -----------------------
                elif "text" in message:
                    payload = json.loads(message["text"])
                    print("[WS EVENT]", payload)

        except WebSocketDisconnect:
            print(f"[WS] Interview session ended: {session_id}")

    async def _send_response(self, ws: WebSocket, text: str):
        """
        Send avatar text, visemes, and audio.
        """

        # TTS
        audio_bytes = self.tts.synthesize(text)

        # Estimate duration (rough heuristic)
        duration_ms = int(len(audio_bytes) / 32)

        # Visemes
        visemes = self.viseme.generate(duration_ms)

        # Send avatar sync
        await ws.send_text(json.dumps({
            "type": "avatar_sync",
            "text": text,
            "visemes": visemes,
        }))

        # Send audio
        await ws.send_bytes(audio_bytes)
