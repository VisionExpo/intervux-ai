# Intervux AI - Architecture

## Purpose
Intervux AI is a distributed interview platform that runs real-time AI-led interviews and supports recruiter decision-making with analytics and reports.

## Component Model

- Frontend (`frontend/`)
  - React + Vite + TypeScript
  - Candidate and recruiter UIs
  - Auth client and hash-based routing
  - Interview WebSocket client (`useInterview`)
- Backend (`backend/`)
  - FastAPI app (`main.py`)
  - REST APIs for auth, candidate workflows, recruiter dashboards
  - WebSocket interview gateway and metrics socket
  - Session/engine orchestration for live interviews
  - AI services (STT/TTS/LLM orchestration)
  - SQLAlchemy models and DB access
  - Celery app/tasks for background processing
- Data/infra
  - PostgreSQL for domain + telemetry persistence
  - Redis as Celery broker/result backend
  - Celery worker + Flower monitoring
  - Docker Compose orchestration

## Runtime Data Flow

1. User authenticates through FastAPI auth routes.
2. Candidate starts mock interview via REST.
3. Frontend opens `/ws/interview` with JWT token.
4. Gateway creates `InterviewSession` and delegates AI logic to `InterviewEngine`.
5. Resume and audio streams are processed by parser/STT services and LLM evaluator.
6. Results, reports, and telemetry are persisted and exposed to dashboards.

## Key Subsystems

- API and auth:
  - `backend/api/routes/auth_routes.py`
  - `backend/api/routes/candidate_routes.py`
- Real-time interview:
  - `backend/sockets/interview_gateway.py`
  - `backend/sessions/interview_session.py`
  - `backend/engines/interview_engine.py`
- AI orchestration:
  - `backend/core/llm_brain.py`
  - `backend/services/stt_service.py`
  - `backend/services/tts_service.py`
  - `backend/core/agent_ocr.py`
- Background:
  - `backend/core/celery_app.py`
  - `backend/core/celery_tasks.py`
- Persistence:
  - `backend/db/database.py`
  - `backend/models/*.py`

## Operational Topology

```text
Frontend (React/Vite)
  -> FastAPI (REST + WebSocket)
      -> PostgreSQL (domain + metrics tables)
      -> Redis (Celery broker/backend)
          -> Celery Worker (async tasks)
          -> Flower (queue/worker monitoring)
      -> AI Services (Gemini/local LLM, STT, TTS)
```

## Reliability Controls (current)

- Startup readiness and health checks (`/health`, `/ready`)
- Runtime metrics and monitor loop (`/metrics`, `/ws/metrics`)
- WebSocket rate limits, timeouts, session cleanup
- Bounded buffers/queues in interview and metrics pipeline
- Celery late ACK + visibility timeout + worker recycling
- SQLAlchemy pool pre-ping/recycle settings

## Known Architectural Gaps

- Multiple resume parsing paths (Gemini and text parser) should be unified under one strategy contract.
- Transcript and turn persistence is not fully centralized for every live interview.
- Frontend uses hash routing with mixed link styles; route normalization is still needed.

