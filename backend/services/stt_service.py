import os
import tempfile
from typing import Union

from backend.core.audio_stack import AudioEngine


class STTService:
    """
    Speech-to-Text service wrapper.
    Converts audio bytes into transcribed text.
    """

    def __init__(self):
        # Load AudioEngine once (Whisper is heavy)
        self.audio_engine = AudioEngine()

    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribes raw audio bytes into text.
        """

        # Write audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp:
            audio_path = tmp.name
            tmp.write(audio_bytes)

        try:
            text = self.audio_engine.speech_to_text(audio_path)
            return text

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)
