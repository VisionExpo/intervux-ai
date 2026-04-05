import asyncio
import io
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from backend.core.logging.logger import get_logger
from backend.services.viseme_service import VisemeService

logger = get_logger(__name__)
viseme_service = VisemeService()

try:
    import pyttsx3
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None

try:
    import azure.cognitiveservices.speech as speechsdk
except Exception:  # pragma: no cover - optional dependency
    speechsdk = None

import httpx

# Use /app/static for Docker, or ./backend/static for local development
if os.path.exists("/app"):
    STATIC_DIR = Path("/app/static/audio")
else:
    STATIC_DIR = Path("backend/static/audio")

STATIC_DIR.mkdir(parents=True, exist_ok=True)


def _cleanup_static_audio_files() -> None:
    """Best-effort cleanup for legacy static audio artifacts."""
    ttl_seconds = int(os.getenv("TTS_STATIC_TTL_SECONDS", "3600"))
    max_files = int(os.getenv("TTS_STATIC_MAX_FILES", "500"))
    now = time.time()

    files = sorted(STATIC_DIR.glob("*.wav"), key=lambda path: path.stat().st_mtime)
    for path in files:
        try:
            if now - path.stat().st_mtime > ttl_seconds:
                path.unlink(missing_ok=True)
        except Exception:
            logger.debug("Static audio cleanup failed for %s", path, exc_info=True)

    files = sorted(STATIC_DIR.glob("*.wav"), key=lambda path: path.stat().st_mtime)
    overflow = len(files) - max_files
    if overflow > 0:
        for path in files[:overflow]:
            try:
                path.unlink(missing_ok=True)
            except Exception:
                logger.debug("Static audio overflow cleanup failed for %s", path, exc_info=True)


class LocalTTSService:
    """
    Local fallback Text-to-Speech service using pyttsx3.
    """

    _engine_lock = threading.Lock()

    def __init__(self, voice: Optional[str] = None):
        self.enabled = pyttsx3 is not None
        self.engine = pyttsx3.init() if self.enabled else None
        if voice and self.engine is not None:
            self.engine.setProperty("voice", voice)

    def synthesize_to_wav_bytes(self, text: str) -> bytes:
        if not self.enabled or self.engine is None:
            return b""

        filename = f"{uuid.uuid4()}.wav"
        filepath = str(STATIC_DIR / filename)

        try:
            with self._engine_lock:
                self.engine.save_to_file(text, filepath)
                self.engine.runAndWait()

            with open(filepath, "rb") as file_handle:
                return file_handle.read()
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)


class AzureNativeTTSService:
    """
    Azure Neural TTS that emits native viseme events.
    """

    def __init__(self):
        self.subscription_key = os.getenv("AZURE_SPEECH_KEY", "").strip()
        self.region = os.getenv("AZURE_SPEECH_REGION", "").strip()
        self.voice = os.getenv("AZURE_SPEECH_VOICE", "en-US-JennyNeural").strip()

    @property
    def is_enabled(self) -> bool:
        return bool(self.subscription_key and self.region and speechsdk is not None)

    def synthesize_with_visemes(self, text: str) -> Tuple[bytes, List[Dict[str, int]]]:
        if speechsdk is None:
            raise RuntimeError("Azure speech SDK is not available")

        speech_config = speechsdk.SpeechConfig(
            subscription=self.subscription_key,
            region=self.region,
        )
        speech_config.speech_synthesis_voice_name = self.voice
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
        )

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        raw_events: List[Tuple[int, int]] = []

        def on_viseme(evt):
            viseme_id = int(getattr(evt, "viseme_id", 0))
            audio_offset = int(getattr(evt, "audio_offset", 0))
            raw_events.append((audio_offset, viseme_id))

        synthesizer.viseme_received.connect(on_viseme)

        result = synthesizer.speak_text_async(text).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            details = getattr(result, "cancellation_details", None)
            message = getattr(details, "error_details", "Azure TTS failed") if details else "Azure TTS failed"
            raise RuntimeError(message)

        audio_bytes = bytes(result.audio_data)
        visemes = _convert_azure_events_to_timeline(raw_events)
        return audio_bytes, visemes


_local_tts = LocalTTSService()

class ElevenLabsTTSService:
    """
    ElevenLabs API integration for premium voice synthesis.
    """
    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "").strip()
        # Default to a generic voice if not specified (e.g. 'Rachel': 21m00Tcm4TlvDq8ikWAM)
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM").strip()
        self.url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"

    @property
    def is_enabled(self) -> bool:
        return bool(self.api_key)

    async def synthesize(self, text: str) -> bytes:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=data, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.content

_elevenlabs_tts = ElevenLabsTTSService()


async def _edge_tts_bytes(text: str) -> bytes:
    """Synthesize speech via Edge TTS and return raw audio bytes."""
    import edge_tts

    voice = os.getenv("EDGE_TTS_VOICE", "en-US-AriaNeural")
    communicate = edge_tts.Communicate(text, voice)
    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])
    return buf.getvalue()


def synthesize_speech_with_visemes(text: str) -> Tuple[bytes, List[Dict[str, int]]]:
    """
    Synthesize speech and return (audio_bytes, viseme_timeline).
    Primary: Edge TTS (free, no account required).
    Fallback: pyttsx3 local TTS.
    Azure TTS is disabled - set AZURE_SPEECH_KEY to re-enable manually.
    """
    audio_bytes = b""

    # Primary: ElevenLabs TTS
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                if _elevenlabs_tts.is_enabled:
                    audio_bytes = pool.submit(asyncio.run, _elevenlabs_tts.synthesize(text)).result(timeout=30)
                else:
                    audio_bytes = pool.submit(asyncio.run, _edge_tts_bytes(text)).result(timeout=30)
        else:
            if _elevenlabs_tts.is_enabled:
                audio_bytes = asyncio.run(_elevenlabs_tts.synthesize(text))
            else:
                audio_bytes = asyncio.run(_edge_tts_bytes(text))
    except Exception:
        logger.warning("ElevenLabs/Edge TTS failed, falling back to pyttsx3", exc_info=True)

    # Fallback: pyttsx3
    if not audio_bytes:
        try:
            audio_bytes = _local_tts.synthesize_to_wav_bytes(text)
        except Exception:
            logger.warning("pyttsx3 fallback also failed", exc_info=True)

    if not audio_bytes:
        return b"", []

    # Generate duration-based viseme timeline
    # Edge TTS returns MP3 (~16kbps); estimate duration from size
    estimated_ms = max(1200, int(len(audio_bytes) / 2000 * 1000))
    visemes = viseme_service.generate_timeline(estimated_ms)
    return audio_bytes, visemes


def synthesize_speech(text: str) -> str:
    """
    Backward-compatible API that writes a WAV to static path.
    """
    audio_bytes, _ = synthesize_speech_with_visemes(text)
    _cleanup_static_audio_files()

    filename = f"{uuid.uuid4()}.wav"
    filepath = str(STATIC_DIR / filename)

    with open(filepath, "wb") as file_handle:
        file_handle.write(audio_bytes)

    return f"/static/audio/{filename}"


def _convert_azure_events_to_timeline(raw_events: List[Tuple[int, int]]) -> List[Dict[str, int]]:
    """
    Azure viseme audio_offset is in 100ns ticks.
    """
    if not raw_events:
        return []

    sorted_events = sorted(raw_events, key=lambda item: item[0])
    timeline: List[Dict[str, int]] = []

    for idx, (offset_ticks, viseme_id) in enumerate(sorted_events):
        start_ms = max(0, int(offset_ticks / 10000))
        if idx + 1 < len(sorted_events):
            end_ms = max(start_ms + 16, int(sorted_events[idx + 1][0] / 10000))
        else:
            end_ms = start_ms + 120

        timeline.append(
            {
                "start": start_ms,
                "end": end_ms,
                "viseme": int(viseme_id),
            }
        )

    return timeline
