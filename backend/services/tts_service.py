import os
import tempfile
import wave
import threading
import uuid
from typing import Optional
from pathlib import Path

import numpy as np
import pyttsx3


# Define and create the static directory for audio files
STATIC_DIR = Path("/app/static/audio")
STATIC_DIR.mkdir(parents=True, exist_ok=True)


class TTSService:
    """
    Local Text-to-Speech service using pyttsx3.
    NOTE:
    This is synchronous and CPU-bound.
    Suitable for demos and low concurrency.
    """

    _engine_lock = threading.Lock()

    def __init__(self, voice: Optional[str] = None):
        self.engine = pyttsx3.init()
        if voice:
            self.engine.setProperty("voice", voice)

    def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech and return Float32 PCM bytes.
        """

        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp:
            wav_path = tmp.name

        try:
            # pyttsx3 is NOT thread-safe
            with self._engine_lock:
                self.engine.save_to_file(text, wav_path)
                self.engine.runAndWait()

            return self._wav_to_float32_pcm(wav_path)

        finally:
            if os.path.exists(wav_path):
                os.remove(wav_path)

    @staticmethod
    def _wav_to_float32_pcm(wav_path: str) -> bytes:
        """
        Convert WAV file to Float32 PCM bytes (mono).
        """
        with wave.open(wav_path, "rb") as wf:
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
            audio /= 32768.0  # normalize to [-1, 1]

        return audio.tobytes()


# --- v1.0 Public Function ---

_tts_service_instance = TTSService()


def synthesize_speech(text: str) -> str:
    """
    Synthesizes speech, saves it as a static WAV file,
    and returns the URL path for the client to fetch.
    """
    filename = f"{uuid.uuid4()}.wav"
    filepath = str(STATIC_DIR / filename)

    with _tts_service_instance._engine_lock:
        _tts_service_instance.engine.save_to_file(text, filepath)
        _tts_service_instance.engine.runAndWait()

    return f"/static/audio/{filename}"
