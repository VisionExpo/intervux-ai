from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.websocket("/ws/interview")
async def interview_socket(ws: WebSocket):
    await ws.accept()
    print("✅Client connected")

    try:
        while True:
            message = await ws.receive()

            # 🎧 Audio from Frontend
            if "bytes" in message:
                pass
            
            # 🧠 Text / Events
            if "text" in message:
                data = json.loads(message["text"])
                print("Received:",data)

                # Temp AI response (TEMP)
                await ws.send_text(json.dumps({
                    "type": "avatar_sync",
                    "text": "Hello, I am your interviewer. Tell me about yourself.",
                }))

                # 🔊 Temp audio responce(Beep)
                audio_bytes = generate_beep()
                await ws.send_bytes(audio_bytes)

    except WebSocketDisconnect:
        print("❌Client disconnected")


def generate_beep(
        duration_sec: float = 0.4,
        frequency: float = 440.0,
        sample_rate: int = 44100
) -> bytes:
    """
    Generate a short sine-wave beep as Float32 PCM
    """
    t =  np.linspace(0, duration_sec, int(sample_rate*duration_sec), False)
    tone = 0.3 * np.sin(2 * np.pi * frequency * t)

    return tone.astype(np.float32).tobytes()