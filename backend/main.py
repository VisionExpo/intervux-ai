from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.sockets.interview import InterviewSocket

app = FastAPI(title="Intervux AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interview_socket = InterviewSocket()


@app.websocket("/ws/interview")
async def interview_ws(ws: WebSocket):
    """
    Main WebSocket endpoint for real-time interviews.
    """
    await interview_socket.handle(ws)
    print("✅Client connected")

    try:
        while True:
            message = await ws.receive()

            # 🎧 Audio from Frontend
            if "bytes" in message:
                continue
            
            # Temp interviewer response
            interviewer_text = (
                "Hello. I am your interviewer. "
                "Please introduce yourself."
            )

            # Send Text (TEMP)
            await ws.send_text(json.dumps({
                "type": "avatar_sync",
                "text": interviewer_text,
                "viseme": {
                    "type": "speech",
                    "duration_ms": 2000
                }
            }))

            # 🔊 Send real TTS audio
            audio_bytes = synthesize_speech(interviewer_text)
            await ws.send_bytes(audio_bytes)

    except WebSocketDisconnect:
        print("❌Client disconnected")