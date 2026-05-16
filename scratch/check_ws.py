from fastapi import WebSocket
from starlette.websockets import WebSocketState

def check_ws_states():
    print(f"WebSocketState.CONNECTING: {WebSocketState.CONNECTING}")
    print(f"WebSocketState.CONNECTED: {WebSocketState.CONNECTED}")
    print(f"WebSocketState.DISCONNECTED: {WebSocketState.DISCONNECTED}")

if __name__ == "__main__":
    check_ws_states()
