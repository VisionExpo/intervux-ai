import asyncio
import websockets
import sys

async def test_connect():
    uri = "ws://127.0.0.1:8000/ws/metrics?token=test-token"
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected!")
            greeting = await websocket.recv()
            print(f"Received: {greeting}")
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    asyncio.run(test_connect())
