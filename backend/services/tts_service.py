import pyttsx3
import numpy as np
import tempfile
import wave
import os

engine = pyttsx3.init()

def synthesize_speech(text: str) -> bytes:
    """
    Convert text to speech and return Float32  PCM bytes
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        filename = tmp.name


    engine.save_to_file(text, filename)
    engine.runAndWait()

    pcm_audio = wav_to_float32_pcm(filename)
    os.remove(filename)

    return pcm_audio


def wav_to_float32_pcm(wav_path: str) -> bytes:
    with wave.open(wav_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        audio /= 32768.0 # normalize to [-1, 1]

    return audio.tobytes