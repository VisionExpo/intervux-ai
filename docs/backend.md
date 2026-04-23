# Backend Architecture

The Intervux AI backend is built with FastAPI using an **App Factory Pattern** to ensure modularity, testability, and production-grade maintenance.

## 🏗 Modular Structure

### 1. Module: Interview
- **Purpose**: Manages the real-time interview lifecycle.
- **Key Files**:
    - `backend/modules/interview/websocket/interview_gateway.py`: WS Orchestration.
    - `backend/modules/interview/sessions/interview_session.py`: Session Logic & Lazy Persistence.
- **Responsibilities**: Connection handling, audio buffering, phase transitions.

### 2. Module: Evaluation
- **Purpose**: Deep analysis of interview transcripts.
- **Key Files**:
    - `backend/services/evaluation_service.py`: Orchestration.
    - `backend/core/evaluation_engine.py`: Reasoning analysis.
- **Responsibilities**: Multi-pass scoring, consistency checking, final report generation.

### 3. Module: Candidate
- **Purpose**: Candidate portal and profile management.
- **Key Files**:
    - `backend/modules/candidate/routes/candidate_routes.py`.
    - `backend/modules/candidate/routes/resume_routes.py`.
- **Responsibilities**: Profile updates, resume uploads, interview history.

### 4. Module: Recruiter
- **Purpose**: Recruitment management and dashboard.
- **Key Files**:
    - `backend/modules/recruiter/routes/recruiter_routes.py`.
- **Responsibilities**: Job creation, candidate evaluation review, pipeline management.

### 5. Module: Infrastructure & Core
- **Purpose**: System-wide cross-cutting concerns.
- **Key Files**:
    - `backend/infrastructure/bootstrap.py`: Lifecycle orchestration.
    - `backend/api/middleware/`: Security, Observability, Error Handling.
- **Responsibilities**: DB migrations, LLM pre-warming, structured logging, request tracing.

## 🔄 Internal Flow: Request-Response Lifecycle

1.  **Middleware Processing**: Every request passes through `ObservabilityMiddleware` (timing/tracing) and `SecurityHeadersMiddleware`.
2.  **Routing**: Routes are grouped by domain (e.g., `/api/auth`, `/api/candidate`).
3.  **Service Layer**: Controllers delegate business logic to specialized services (e.g., `TTSService`, `LLMService`).
4.  **Error Handling**: Global exception handlers catch domain-specific errors and return standardized JSON payloads.

## 🛡 Security & Reliability
- **Pydantic v2**: Strict type validation at the API boundary.
- **JWT Authentication**: Secure token-based access control.
- **Circuit Breakers**: Implemented in the LLM layer to handle provider outages gracefully.
