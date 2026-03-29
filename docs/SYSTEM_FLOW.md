# Intervux AI - System Flow

## 1. System Overview

Intervux AI is an interview platform that combines a candidate-facing interview experience with recruiter analytics and AI-driven evaluation.

At runtime, the platform has two major planes:

- Candidate experience plane:
  - React + Vite frontend
  - Authenticated candidate dashboard
  - Resume upload
  - Real-time WebSocket interview session with avatar/audio
- Recruiter and operations plane:
  - FastAPI REST APIs
  - Evaluation dashboard and decision support
  - PostgreSQL persistence
  - Redis + Celery background processing
  - Flower monitoring

AI capabilities are used across the flow:

- Resume parsing/entity extraction
- Speech-to-text (STT) from streamed interview audio
- LLM-based question generation and answer evaluation
- Text-to-speech (TTS) and viseme timeline for avatar output

---

## 2. High-Level Architecture

### Runtime interaction model

- Frontend calls FastAPI over REST for auth/profile/dashboard/interview setup.
- Frontend uses WebSocket (`/ws/interview`) for real-time interview IO.
- FastAPI persists domain data and telemetry in PostgreSQL.
- Celery workers consume jobs via Redis broker.
- Flower monitors Celery workers and queues.

### Core backend components

- API app: `backend/main.py`
- Auth routes: `backend/api/routes/auth_routes.py`
- Candidate routes: `backend/api/routes/candidate_routes.py`
- Interview WebSocket gateway: `backend/sockets/interview_gateway.py`
- Session manager: `backend/sessions/interview_session.py`, `backend/sessions/registry.py`
- Interview engine: `backend/engines/interview_engine.py`
- LLM orchestration: `backend/core/llm_brain.py`
- STT/TTS services: `backend/services/stt_service.py`, `backend/services/tts_service.py`
- Resume parsing services:
  - Vision path: `backend/core/agent_ocr.py` (Gemini file parsing)
  - Text parser path: `backend/resume_parser/services.py`
- Celery app/tasks: `backend/core/celery_app.py`, `backend/core/celery_tasks.py`

### Infra/runtime

- `docker-compose.yaml` runs `postgres`, `redis`, `backend`, `worker`, `flower`.
- `Dockerfile` builds backend and worker image from one code path.

---

## 3. Complete User Flow (Candidate Interview Flow)

### End-to-end sequence

1. Candidate login
   - Frontend login form posts to `POST /api/auth/login`.
   - Access token is stored in `localStorage`.
   - Frontend fetches `GET /api/auth/me` to resolve role/profile.

2. Dashboard load
   - Candidate route loads `GET /api/candidate/dashboard` and `GET /api/candidate/profile`.
   - UI shows resume status, remaining mock interviews, recent activity.

3. Start mock interview
   - Frontend calls `POST /api/candidate/mock-interview/start`.
   - Backend creates `mock_interviews` record (`in_progress`) and decrements remaining credits.
   - Frontend navigates to `#/interview-session`.

4. WebSocket interview session start
   - `useInterview` opens `ws://localhost:8000/ws/interview?token=...`.
   - Gateway validates token, applies IP/session limits, creates a new session, registers it.

5. Greeting from AI interviewer
   - Gateway emits avatar sync + TTS audio/visemes greeting.
   - Session moves to `WAITING_RESUME`.

6. Resume upload (inside interview session)
   - Frontend sends `{"type":"resume_upload","file_name","file_bytes"}` over WebSocket.
   - Session calls interview engine start flow.

7. Resume parsing and profile generation
   - Engine decodes base64 and calls `parse_resume_bytes` (Gemini parser path).
   - Parsed profile is loaded into interview state and used for skill map/coverage context.

8. First question generation
   - Engine generates first adaptive question using profile + memory + difficulty policy.
   - Gateway sends question text and avatar TTS audio.

9. Answer capture
   - Frontend `MediaRecorder` streams binary audio chunks over WebSocket.
   - Session buffers chunks and emits partial transcripts intermittently.

10. STT + evaluation scoring
    - On `stream_end`, buffered audio is transcribed.
    - Engine evaluates answer via evaluation service/LLM pipeline.
    - Scores/feedback are returned to client.

11. Next-question decision
    - Engine updates memory, topic scores, skill coverage, difficulty.
    - If continue criteria pass, next question is generated and sent.
    - Otherwise interview completes.

12. Interview completion + final report
    - Engine generates final report.
    - WebSocket sends completion payload.
    - Session cleanup runs and registry entry is removed.

---

## 4. Resume Processing Pipeline

Intervux currently has multiple resume ingestion paths.

### A) Candidate profile upload path (active)

Frontend upload  
-> `POST /api/candidate/resume`  
-> file saved under `uploads/resumes/<user>/...`  
-> parsed via `backend/core/agent_ocr.py::parse_resume` (Gemini vision parser)  
-> skills/score/profile fields computed  
-> `candidate_profiles` updated  
-> notification inserted  
-> response returned to frontend

### B) Interview WebSocket resume path (active)

WebSocket `resume_upload` message  
-> `InterviewSession._handle_resume_upload`  
-> `InterviewEngine.start_interview`  
-> `parse_resume_bytes` (Gemini parser)  
-> `InterviewState.profile` set  
-> question generation starts

### C) Celery resume parsing path (implemented, optional wiring)

`backend.core.celery_tasks.parse_resume`  
-> `backend.resume_parser.services.parse_resume_service`  
-> file text extraction (`pdfplumber/docx/txt`)  
-> basic entity/skills extraction (`spaCy` + keyword matching)  
-> structured payload returned

Note: the candidate API currently uses the Gemini parser path directly, while Celery resume parsing exists as a background-capable pathway.

---

## 5. WebSocket Interview Engine Flow

Lifecycle for `/ws/interview`:

1. Client connects with token query param.
2. Gateway verifies token and rate limits by IP.
3. WebSocket accepted and session slot acquired.
4. `InterviewSession` created and registered.
5. Greeting + avatar sync + TTS emitted.
6. Session enters main message loop:
   - `resume_upload` -> parse resume -> first question
   - binary `audio_chunk` -> buffer + partial transcript
   - `stream_end` -> STT + evaluation + next question or completion
7. On disconnect/timeout/error:
   - session cleanup
   - registry unregister
   - active session counters released

Safety controls in current flow:

- receive/send timeouts
- max concurrent sessions
- per-IP connection attempt limiting
- bounded audio buffer with overflow handling
- hard cap on maximum interview turns

---

## 6. AI Processing Pipeline

### Resume AI

- `agent_ocr.py` uses Gemini (`gemini-2.5-flash`) to parse resume files into structured profile data.
- Local temp file and uploaded artifact cleanup are performed.

### STT

- `stt_service.py` lazily initializes `AudioEngine` with faster-whisper backend.
- In-memory byte transcription is preferred, with fallback strategies.
- STT latency metrics are recorded.

### TTS + avatar

- `tts_service.py` supports:
  - Azure Neural TTS + native visemes (if configured)
  - local pyttsx3 fallback
- Gateway sends `avatar_sync` and `avatar_visemes` events plus binary WAV payloads.

### LLM generation/evaluation

- `llm_brain.py` handles:
  - question generation
  - next-question generation
  - answer evaluation
  - final report generation
- Includes provider fallback (`gemini` <-> local qwen/ollama), circuit breaker, and multi-pass evaluation features.
- `decision_support_service.py` produces recruiter-oriented summary/recommendation reports.

---

## 7. Celery Worker Pipeline

Celery components:

- App config: `backend/core/celery_app.py`
- Tasks: `backend/core/celery_tasks.py`
- Broker/backend: Redis
- Monitoring: Flower

Key task families:

- Resume parsing: `parse_resume`, `parse_resume_from_text`
- Evaluation/report: `generate_evaluation`, `generate_evaluation_async`, `generate_report`
- Analytics/ops: `aggregate_analytics`, `cleanup_old_logs`
- Alerts/export: `dispatch_alert`, `export_data`

Worker behavior highlights:

- task time limits
- late ACK + reject-on-worker-lost
- visibility timeout
- task routing to dedicated queues (`resumes`, `evaluations`, `reports`)

---

## 8. Database Interactions

Primary PostgreSQL tables/models:

- Identity/platform:
  - `users`, `revoked_tokens`, `api_keys`
- Candidate portal:
  - `candidate_profiles`, `mock_interviews`, `notifications`
- Recruiter/hiring:
  - `job_posts`, `job_skills`, `candidates`, `interviews`, `interview_questions`, `interview_replay_segments`
- Telemetry/experiments:
  - `llm_metrics`, `experiments`

Data usage patterns:

- REST endpoints use SQLAlchemy sessions via `get_db` or `SessionLocal`.
- Dashboard endpoints aggregate both DB metrics and in-memory runtime metrics.
- Telemetry service writes evaluation metrics to JSONL + `llm_metrics`.

---

## 9. Error Handling Flow

### Resume parsing failure

- API path: route catches parse exception, falls back to default parsed payload or HTTP error.
- WebSocket path: session returns recoverable error message when bootstrap fails.

### WebSocket disconnect

- `WebSocketDisconnect` is handled in gateway and metrics sockets.
- Session cleanup and unregister execute in `finally`.

### STT failure

- STT service records error metrics and logs exceptions.
- Fallback paths attempt alternate decode/transcription routes.

### LLM timeout/provider failure

- LLM provider errors are logged.
- Fallback provider may be used if configured.
- Circuit breaker can open on repeated failures/slow calls.
- Final fallback returns safe default evaluation/report payload.

---

## 10. Monitoring and Observability

Built-in observability includes:

- Health endpoints:
  - `GET /health`
  - `GET /ready`
- Runtime metrics endpoint:
  - `GET /metrics`
- Real-time metrics socket:
  - `WS /ws/metrics`
- Runtime monitor:
  - periodic gauges (active sessions, queue depth, GPU mem, STT spikes)
- Request middleware metrics:
  - request count, errors, latency
- Telemetry persistence:
  - JSONL logs
  - PostgreSQL `llm_metrics`
- Celery visibility:
  - Flower UI on port 5555

---

## 11. System Diagram

```text
                         +----------------------+
                         |  React + Vite Frontend|
                         | (Auth, Dashboard, WS) |
                         +-----------+----------+
                                     |
                       REST + WebSocket (/ws/interview, /ws/metrics)
                                     |
                    +----------------v----------------+
                    |         FastAPI Backend         |
                    | routes + interview gateway      |
                    | session manager + engine        |
                    +--------+--------------+---------+
                             |              |
                             |              |
                  +----------v---+      +---v-------------------+
                  | PostgreSQL    |      | Redis (broker/backend)|
                  | users/interviews|    | Celery queues/results |
                  +----------+---+      +---+-------------------+
                             |              |
                             |              |
                    +--------v--------------v--------+
                    |         Celery Workers         |
                    | resume/eval/report/analytics   |
                    +--------+--------------+--------+
                             |              |
                  +----------v--+      +----v--------------------+
                  | AI Services  |      | Flower + Runtime Metrics |
                  | STT / TTS /  |      | health + logs + gauges   |
                  | LLM eval/gen |      +---------------------------+
                  +--------------+
```

---

## 12. Known Limitations

1. Multiple resume pipelines are active in parallel.
- Candidate/profile flow and interview flow use Gemini parser path.
- Celery resume parser uses a separate text-extraction/entity pipeline.
- Behavior and extracted schema quality can diverge between paths.

2. Candidate resume upload is currently synchronous in API.
- Long parse times can hold request duration unless moved to Celery dispatch path.

3. Mixed persistence of interview outcomes.
- Runtime interview state is in-memory session object.
- Not every WebSocket interview turn is guaranteed to be persisted as durable interview rows.

4. WebSocket contract and gateway implementation need tighter alignment.
- There is a call to `_send_evaluation_response(...)` in the gateway path that should be verified against current implementation.

5. Frontend routing is hash-based and partially inconsistent.
- Some links use hash routes, others plain paths.
- This can cause navigation drift in browser refresh/direct-link scenarios.

6. AI dependency availability is environment-sensitive.
- External APIs (Gemini/Azure) and local model runtimes (ollama/local LLM) can affect behavior if not consistently configured.

7. Operational scaling policies are basic.
- Current stack includes health checks and worker controls, but autoscaling and stronger distributed session/state strategies are not yet implemented.

