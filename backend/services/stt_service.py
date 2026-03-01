import os
import tempfile
import time

from backend.core.audio_stack import AudioEngine
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)


class STTService:
    """
    Speech-to-Text service wrapper.
    Converts audio bytes into transcribed text.
    """

    def __init__(self):
        self.audio_engine = AudioEngine()

    def transcribe(self, audio_file) -> str:
        start_time = time.time()

        try:
            audio_bytes = audio_file.file.read()

            if not audio_bytes:
                logger.warning("Empty audio file received")
                metrics.record_error()
                return ""

            file_size_kb = round(len(audio_bytes) / 1024, 2)

            with tempfile.NamedTemporaryFile(
                suffix=".wav", delete=False
            ) as tmp:
                audio_path = tmp.name
                tmp.write(audio_bytes)

            try:
                text = self.audio_engine.speech_to_text(audio_path)
                text = text.strip()

                duration = round(time.time() - start_time, 3)
                metrics.record_latency("stt_processing", duration)

                logger.info(
                    "STT completed",
                    extra={
                        "extra_data": {
                            "file_size_kb": file_size_kb,
                            "transcript_length": len(text),
                            "duration": duration
                        }
                    }
                )

                # Basic transcript validation
                if len(text) < 3:
                    logger.warning("Very short transcript detected")

                return text

            finally:
                if os.path.exists(audio_path):
                    os.remove(audio_path)

        except Exception as e:
            metrics.record_error()
            logger.exception("STT processing failed")
            raise


# --- Singleton instance ---
_stt_service_instance = STTService()


def transcribe_audio(audio_file) -> str:
    return _stt_service_instance.transcribe(audio_file)


def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """
    Transcribe raw audio bytes received via WebSocket.
    """
    start_time = time.time()

    if not audio_bytes:
        logger.warning("Empty audio bytes received")
        metrics.record_error()
        return ""

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        audio_path = tmp.name
        tmp.write(audio_bytes)

    try:
        text = _stt_service_instance.audio_engine.speech_to_text(audio_path)
        text = text.strip()

        duration = round(time.time() - start_time, 3)
        metrics.record_latency("stt_processing", duration)

        logger.info(
            "STT completed from bytes",
            extra={
                "extra_data": {
                    "file_size_kb": round(len(audio_bytes) / 1024, 2),
                    "transcript_length": len(text),
                    "duration": duration
                }
            }
        )

        return text
    except Exception:
        metrics.record_error()
        logger.exception("STT byte processing failed")
        raise
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)
