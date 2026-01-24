import os
import asyncio
import edge_tts
import whisper
import torch
from pydub import AudioSegment

# 1. GPU Optimization
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🚀 Audio Stack is running on {DEVICE}")


class AudioEngine:
    def __init__(self):
        # Load Whisper Model once (It's heavy! so we will cache it)
        print("🎤 Loading Whisper Model...")
        self.stt_model = whisper.load_model("base", device=DEVICE)

    async def text_to_speech(self, text, output_file="temp_output.mp3"):
        """
        Convert text to audio using EdgeTTS
        Voice : en-US-AriaNeural (Female) or en_US-ChristopherNeural (Male)
        """
        voice = "en-US-AriaNeural"
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return output_file
    
    def speech_to_text(self, audio_file_path):
        """
        Transcribe audio file to text using Whisper on GPU
        """ 
        # Whisper handles ffmpeg processing internally
        result = self.stt_model.transcribe(audio_file_path, fp16=(DEVICE=="cuda"))
        return result["text"]


# --- Testing Block ---
if __name__ == "__main__":
    # Test TTS
    engine = AudioEngine()
    
    print("🗣️ Testing TTS...")
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(engine.text_to_speech("Hello candidate, welcome to PrepMaster."))
    print("✅ TTS Generated: temp_output.mp3")