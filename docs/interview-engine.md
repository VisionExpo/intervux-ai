# Interview Engine

The Interview Engine is the stateful orchestration layer that drives the interactive candidate experience. It combines a robust state machine with real-time WebSocket communication.

## 🧠 The State Machine
The interview follows a strict lifecycle managed by the `InterviewState` model:

1.  **`WAITING_RESUME`**: Initial state where the avatar introduces itself and requests a resume.
2.  **`PROCESSING_RESUME`**: Temporary state while the LLM parses the resume to build a question plan.
3.  **`QUESTION`**: The avatar is speaking/asking a question.
4.  **`LISTENING`**: The avatar is waiting for candidate input (STT active).
5.  **`THINKING`**: Processing the candidate's answer and generating the next move.
6.  **`COMPLETE`**: Final phase; session ends and evaluation is triggered.

## 📡 WebSocket Flow & Session Lifecycle

### 1. Connection & Hydration
- **Gateway**: `backend/modules/interview/websocket/interview_gateway.py`.
- **Session**: `backend/modules/interview/sessions/interview_session.py`.
- On connection, the Gateway creates/hydrates an `InterviewSession`.

### 2. The Loop
- **Candidate Input**: Audio chunks sent via WS → Buffered in `AudioBuffer` → Sent to Celery for transcription.
- **Engine Decision**: `InterviewEngine.evaluate_answer` analyzes the transcript.
- **Response Generation**: `InterviewEngine.generate_next_question` creates the next interaction.
- **Output Streaming**: TTS Service generates audio & visemes → Streamed back to UI in chunks.

## 🎭 Avatar & Audio Pipeline
To ensure "The Illusion of Life," the audio and visuals must be perfectly synchronized:

1.  **Synthesis**: TTS service returns audio bytes + a **Viseme Timeline**.
2.  **Visemes**: Metadata containing mouth shape IDs and timestamps (e.g., `[{"id": 1, "start": 0}, {"id": 12, "start": 100}]`).
3.  **Synchronization**: The `useInterview.ts` hook receives the audio and visemes. It uses a precise timer to trigger CSS/3D mouth shape changes exactly as the corresponding audio plays.

## 🔗 Code Mapping

### Component: Interview Engine Core
- **Files**: `backend/ai/engines/interview_engine.py`.
- **What it does**: Logic for what question to ask next and how to parse answers.
- **Why it exists**: To separate "Interview Logic" from "Network/Socket Logic."
- **Connects to**: `LLMService` for generation and `InterviewState` for tracking.

### Component: WebSocket Gateway
- **Files**: `backend/modules/interview/websocket/interview_gateway.py`.
- **What it does**: Manages WebSocket connections, authentication, and heartbeat.
- **Why it exists**: To provide a robust, concurrent entry point for real-time traffic.
- **Connects to**: `InterviewSession` for business logic.

### Component: Frontend Interview Hook
- **Files**: `frontend/src/hooks/useInterview.ts`.
- **What it does**: Client-side state machine, audio playback, and viseme synchronization.
- **Why it exists**: To keep the UI responsive and handle network jitter.
- **Connects to**: WebSocket API and 3D Avatar component.

## 🛡 Failure Handling: Disconnects
- **Problem**: Candidate loses internet for 5 seconds.
- **Solution**: The `InterviewSession` persists state to Redis after every phase change (**Lazy Persistence**). Upon reconnection, the session is re-hydrated instantly, and the candidate resumes exactly where they left off without losing progress.
- **Sequence Sync**: Every message carries a monotonic `seq` ID to prevent out-of-order execution in high-jitter environments.
