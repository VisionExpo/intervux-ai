import asyncio
import os
import tempfile
import wave
from io import BytesIO
from typing import Optional

import edge_tts
import numpy as np
import whisper

from backend.config.setting import DEVICE


class AudioEngine:
    """
    Handles Speech-to-Text (Whisper) and Text-to-Speech (Edge TTS).
    """

    def __init__(self, whisper_model: str = "base"):
        print(f"[INFO] Initializing AudioEngine on {DEVICE}")

        # Load Whisper once (heavy model)
        self.stt_model = whisper.load_model(
            whisper_model,
            device=DEVICE
        )

    # ---------------------------
    # Text → Speech
    # ---------------------------

    async def text_to_speech(self, text: str) -> bytes:
        """
        Convert text to speech and return audio bytes (mp3).
        """
        voice = "en-US-AriaNeural"

        with tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False
        ) as tmp:
            output_path = tmp.name

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)

            with open(output_path, "rb") as f:
                return f.read()

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    # ---------------------------
    # Speech → Text
    # ---------------------------

    def speech_to_text(self, audio_path: str) -> str:
        """
        Transcribe an audio file into text.
        """
        result = self.stt_model.transcribe(
            audio_path,
            fp16=(DEVICE == "cuda")
        )
        return result.get("text", "").strip()

    def speech_to_text_wav_bytes(self, audio_bytes: bytes) -> str:
        """
        Fast path for WAV bytes without filesystem roundtrip.
        """
        with wave.open(BytesIO(audio_bytes), "rb") as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())

        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)

        result = self.stt_model.transcribe(
            audio,
            fp16=(DEVICE == "cuda"),
            language="en",
        )
        return result.get("text", "").strip()
