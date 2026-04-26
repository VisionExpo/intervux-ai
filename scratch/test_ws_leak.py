
import asyncio
import anyio
from fastapi import FastAPI, WebSocket
from fastapi.testclient import TestClient
import pytest

app = FastAPI()

@app.websocket("/ws")
async def ws_handler(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except:
        pass

def test_ws_leak():
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            pass # Close immediately

if __name__ == "__main__":
    test_ws_leak()
    print("Done")
