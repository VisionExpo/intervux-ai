import io
import os
import tempfile
import wave
from io import BytesIO

import edge_tts
import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from backend.config.setting import DEVICE


class AudioEngine:
    """
    Handles Speech-to-Text (Whisper) and Text-to-Speech (Edge TTS).
    """

    def __init__(self, whisper_model: str = "base"):
        print(f"[INFO] Initializing AudioEngine on {DEVICE}")

        # Load Whisper once (heavy model)
        # Use DEVICE from settings (automatically falls back to CPU if CUDA unavailable)
        compute_type = "float16" if DEVICE == "cuda" else "int8"
        try:
            self.stt_model = WhisperModel(
                whisper_model,
                device=DEVICE,
                compute_type=compute_type,
            )
        except RuntimeError as e:
            if "CUDA" in str(e):
                print(f"[WARN] CUDA initialization failed: {e}")
                print("[INFO] Falling back to CPU for Whisper")
                self.stt_model = WhisperModel(
                    whisper_model,
                    device="cpu",
                    compute_type="int8",
                )
            else:
                raise

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
        segments, _info = self.stt_model.transcribe(
            audio_path,
            beam_size=1,
            vad_filter=True,
            word_timestamps=False,
        )
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def speech_to_text_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio bytes in-memory to avoid filesystem roundtrips.
        """
        audio_buffer = io.BytesIO(audio_bytes)
        audio, _sample_rate = sf.read(audio_buffer, dtype="float32")
        if audio.ndim > 1:
            audio = audio.mean(axis=1)

        segments, _info = self.stt_model.transcribe(
            audio,
            beam_size=1,
            vad_filter=True,
            word_timestamps=False,
        )
        text = " ".join([segment.text for segment in segments])
        return text.strip()

    def speech_to_text_wav_bytes(self, audio_bytes: bytes) -> str:
        """
        Fast path for WAV bytes without filesystem roundtrip.
        """
        with wave.open(BytesIO(audio_bytes), "rb") as wf:
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())

        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)

        segments, _info = self.stt_model.transcribe(
            audio,
            beam_size=1,
            vad_filter=True,
            word_timestamps=False,
        )
        text = " ".join([segment.text for segment in segments])
        return text.strip()
