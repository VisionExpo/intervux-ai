from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

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
    print("Client connected")

    try:
        while True:
            message = await ws.receive()

            if "bytes" in message:
                # Audio chunk received
                print(f"Audio chunk size: {len(message['bytes'])}")

            if "text" in message:
                data = json.loads(message["text"])
                print("Received:",data)

                # Fake AI response (TEMP)
                await ws.send_text(json.dumps({
                    "type": "avatar_sync",
                    "text": "Hello, I am your interviewer. Tell me about yourself.",
                    "emotion": "neutral"
                }))

    except WebSocketDisconnect:
        print("Client disconnected")
