import asyncio
import io
import os
import threading
import time
import uuid
import base64
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend.core.logging.logger import get_logger
from backend.services.viseme_service import VisemeService

logger = get_logger(__name__)
viseme_service = VisemeService()

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import azure.cognitiveservices.speech as speechsdk
except Exception:
    speechsdk = None

import httpx

# Static directory setup
if os.path.exists("/app"):
    STATIC_DIR = Path("/app/static/audio")
else:
    STATIC_DIR = Path("backend/static/audio")

STATIC_DIR.mkdir(parents=True, exist_ok=True)


class LocalTTSService:
    _engine_lock = threading.Lock()
    def __init__(self, voice: Optional[str] = None):
        self.enabled = pyttsx3 is not None
        self.engine = pyttsx3.init() if self.enabled else None
        if voice and self.engine is not None:
            self.engine.setProperty("voice", voice)
    def synthesize_to_wav_bytes(self, text: str) -> bytes:
        if not self.enabled or self.engine is None: return b""
        filename = f"{uuid.uuid4()}.wav"; filepath = str(STATIC_DIR / filename)
        try:
            with self._engine_lock:
                self.engine.save_to_file(text, filepath)
                self.engine.runAndWait()
            with open(filepath, "rb") as f: return f.read()
        finally:
            if os.path.exists(filepath): os.remove(filepath)


class TTSService:
    """
    Unified Text-to-Speech service.
    """
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()
        self.edge_voice = os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")
        self.disable_tts = os.getenv("DISABLE_TTS", "false").lower() == "true"
        self._local_tts = LocalTTSService()

    async def synthesize_chunks(self, session_id: str, text: str) -> List[Dict]:
        if self.disable_tts: return []
        from backend.core.celery_tasks import synthesize_tts_task
        segments = self._split_sentences(text)
        celery_tasks = [synthesize_tts_task.delay(seg) for seg in segments]
        
        chunks = []
        for seg, task in zip(segments, celery_tasks):
            deadline = time.time() + 15.0 
            while not task.ready():
                if task.failed() or time.time() > deadline: break
                await asyncio.sleep(0.05)
            result = task.result if task.ready() and not task.failed() else None
            if result:
                b64_audio = result.get("audio_b64", "")
                audio_bytes = base64.b64decode(b64_audio) if b64_audio else b""
                chunks.append({"text": seg, "audio_bytes": audio_bytes, "visemes": result.get("visemes", [])})
        return chunks

    async def synthesize_with_visemes(self, text: str) -> Tuple[bytes, List[Dict[str, int]]]:
        """Core synthesis logic with multi-provider fallback."""
        audio_bytes = b""
        try:
            if self.elevenlabs_api_key:
                audio_bytes = await self._elevenlabs_synth(text)
            else:
                audio_bytes = await self._edge_tts_synth(text)
        except Exception:
            logger.warning("Premium TTS failed, falling back to local", exc_info=True)
            audio_bytes = self._local_tts.synthesize_to_wav_bytes(text)

        if not audio_bytes: return b"", []
        estimated_ms = max(1200, int(len(audio_bytes) / 2000 * 1000))
        visemes = viseme_service.generate_timeline(estimated_ms)
        return audio_bytes, visemes

    async def _elevenlabs_synth(self, text: str) -> bytes:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": self.elevenlabs_api_key}
        data = {"text": text, "model_id": "eleven_monolingual_v1", "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=data, headers=headers, timeout=30.0)
            resp.raise_for_status()
            return resp.content

    async def _edge_tts_synth(self, text: str) -> bytes:
        import edge_tts
        logger.info("Generating TTS (edge-tts) for: %s", text[:100])
        try:
            communicate = edge_tts.Communicate(text, self.edge_voice)
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio": buf.write(chunk["data"])
            audio_bytes = buf.getvalue()
            logger.info("TTS audio generated successfully, size: %s bytes", len(audio_bytes))
            return audio_bytes
        except Exception:
            logger.exception("TTS generation (edge-tts) failed")
            raise

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        clean = (text or "").strip()
        if not clean:
            return []
        parts = re.split(r"(?<=[.!?])\s+", clean)
        return [part.strip() for part in parts if part.strip()] or [clean]

async def synthesize_speech_with_visemes(text: str) -> Tuple[bytes, List[Dict[str, int]]]:
    service = TTSService()
    return await service.synthesize_with_visemes(text)

