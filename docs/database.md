# Database Schema & Persistence

Intervux AI uses a hybrid persistence model: **PostgreSQL** for permanent relational data and **Redis** for ephemeral, high-speed session state.

## 🗄 PostgreSQL Tables

### 1. `users`
- **Role**: Identity management.
- **Fields**: `id`, `email`, `hashed_password`, `role` (CANDIDATE/RECRUITER/ADMIN).

### 2. `candidates`
- **Role**: Candidate profile information.
- **Fields**: `id`, `user_id`, `full_name`, `resume_url`, `skills`, `profile_summary`.

### 3. `mock_interviews` (Main Interview Record)
- **Role**: Tracks the status and results of an interview session.
- **Fields**: 
    - `id`, `candidate_id`, `job_id`.
    - `status` (PENDING, IN_PROGRESS, COMPLETED, FAILED).
    - `transcript` (JSON block of the conversation).
    - `audio_summary` (Reference to stored audio artifacts).
    - `score`, `report` (JSON evaluation data).

### 4. `evaluation_records`
- **Role**: Detailed audit trail for Pass 1-4 of the pipeline.
- **Fields**: `id`, `interview_id`, `reasoning`, `consistency_score`, `raw_llm_output`.

## 🚀 Redis Usage

### 1. Session State (`interview:state_obj:{session_id}`)
- Stores the serialized `InterviewState` and `EvaluationContext`.
- Used for instant re-hydration after network disconnects.

### 2. Cache & Rate Limiting
- Stores WebSocket rate-limit counters.
- Caches common LLM prompts and static settings.

### 3. Message Broker
- Serves as the backbone for Celery workers.

## 🔗 Code Mapping
- **Models**: `backend/models/` (SQLAlchemy/Pydantic).
- **Session Registry**: `backend/modules/interview/sessions/registry.py`.
- **Database Engine**: `backend/db/session.py`.

## 🛠 Why this Design?
Relational databases (PostgreSQL) provide ACID guarantees necessary for permanent career records, while Redis provides the microsecond latency required for real-time WebSocket interactions without saturating the primary database with high-frequency "dirty" writes.
