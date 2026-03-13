import os
import threading
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import pyttsx3
except Exception:  # pragma: no cover - optional dependency
    pyttsx3 = None

try:
    import azure.cognitiveservices.speech as speechsdk
except Exception:  # pragma: no cover - optional dependency
    speechsdk = None

# Use /app/static for Docker, or ./backend/static for local development
if os.path.exists("/app"):
    STATIC_DIR = Path("/app/static/audio")
else:
    STATIC_DIR = Path("backend/static/audio")

STATIC_DIR.mkdir(parents=True, exist_ok=True)


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
_azure_tts = AzureNativeTTSService()


def synthesize_speech_with_visemes(text: str) -> Tuple[bytes, List[Dict[str, int]]]:
    """
    Returns WAV audio bytes and viseme timeline.

    If Azure is configured, use native viseme events.
    Otherwise fallback to local TTS with an empty viseme timeline.
    """
    if _azure_tts.is_enabled:
        try:
            return _azure_tts.synthesize_with_visemes(text)
        except Exception:
            pass

    return _local_tts.synthesize_to_wav_bytes(text), []


def synthesize_speech(text: str) -> str:
    """
    Backward-compatible API that writes a WAV to static path.
    """
    audio_bytes, _ = synthesize_speech_with_visemes(text)

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
