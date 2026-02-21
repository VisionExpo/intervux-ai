import os
import tempfile

from backend.core.audio_stack import AudioEngine


class STTService:
    """
    Speech-to-Text service wrapper.
    Converts audio bytes into transcribed text.
    """

    def __init__(self):
        # Load AudioEngine once (Whisper is heavy)
        self.audio_engine = AudioEngine()

    def transcribe(self, audio_file) -> str:
        """
        Transcribes FastAPI UploadFile into text.
        """

        # Read raw bytes from UploadFile
        audio_bytes = audio_file.file.read()

        if not audio_bytes:
            return ""

        # Write audio bytes to a temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        ) as tmp:
            audio_path = tmp.name
            tmp.write(audio_bytes)

        try:
            text = self.audio_engine.speech_to_text(audio_path)
            return text.strip()

        finally:
            if os.path.exists(audio_path):
                os.remove(audio_path)


# --- v1.0 Public Function ---
_stt_service_instance = STTService()


def transcribe_audio(audio_file) -> str:
    """
    Wrapper function for STT service.
    Accepts FastAPI UploadFile and returns transcribed text.
    """
    return _stt_service_instance.transcribe(audio_file)
