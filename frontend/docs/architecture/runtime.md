# Interview Runtime Architecture

## Purpose
The `InterviewRuntime` is the core brain of the application. It orchestrates the interview session by managing state, media, socket connections, and analytics, completely decoupled from the UI.

## Managers
- **SessionManager**: Handles the lifecycle of the interview.
- **SocketManager**: Manages WebSocket connections for STT and server events.
- **AudioManager**: Manages microphone inputs and TTS audio output.
- **CameraManager**: Manages the local media stream.
- **VisionManager**: Analyzes the camera feed for expression and attention metrics.
- **WorkspaceManager**: Selects the appropriate workspace plugin based on layout.

## Data Flow
The Runtime maintains the `InterviewRuntimeState` and passes a read-only, reactive version of this state down to the `InterviewDashboard` for rendering.
