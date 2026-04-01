# Repository Refactor Audit (Pre-Change)

Date: 2026-04-01
Scope: `intervux-ai` full repository (backend + frontend + infra + docs)

## Summary

- Current backend layout is functional but mixes concerns (`main.py` owns startup + middleware + many domain routes).
- Existing structure partially overlaps target architecture, but domains are not modularized (`recruiter`, `candidate`, `interview`, `evaluation` logic spread across `api`, `services`, `sockets`, `sessions`, `core`).
- Significant repository hygiene issues at root and in source tree (temporary patch scripts, test artifacts, generated files, `__pycache__`, local venv and node_modules committed).
- Duplicate route logic exists in `backend/main.py` and `backend/api/routes/recruiter_dashboard_routes.py`.
- Several backend modules appear unused by runtime imports (`structured_logger`, `audit_service`, `telemetry_service`, `emotion_ai`, `code_engine`).

## Classification Matrix

### KEEP
- `backend/db/alembic/**` (migrations)
- `backend/models/**` (domain schemas + ORM models)
- `backend/services/recruiter_dashboard_store.py`
- `backend/services/evaluation_dashboard_store.py`
- `backend/services/decision_support_service.py`
- `backend/ai/resume_parser/**`
- `backend/ai/engines/interview_engine.py`
- `backend/sockets/metrics.py`
- `backend/sessions/registry.py`
- `backend/services/stt_service.py`
- `backend/services/tts_service.py`
- `backend/services/viseme_service.py`
- `backend/services/audio_buffer.py`
- `frontend/src/**` (except abandoned stylesheet, see DELETE)
- `docker/**`, `Dockerfile`, `docker-compose.yaml`
- `tests/**`

### MERGE
- `backend/main.py` + `backend/api/routes/recruiter_dashboard_routes.py`
  - Action: keep router-based implementation and remove duplicate endpoint declarations from `main.py`.
- Logging stack:
  - `backend/utils/logger.py`
  - `backend/utils/structured_logger.py`
  - Action: centralize logging under `backend/core/logging` and keep compatibility imports.
- Config loading:
  - `backend/config/setting.py`
  - `backend/config/prompt_loader.py`
  - Action: move under `backend/core/config` with compatibility shim.

### MOVE
- `backend/db/database.py` -> `backend/infrastructure/database/database.py`
- `backend/middleware/rate_limiter.py` -> `backend/api/middleware/rate_limiter.py`
- `backend/auth/jwt_service.py` -> `backend/core/security/jwt_service.py`
- `backend/auth/rbac.py` -> `backend/core/security/rbac.py`
- `backend/sockets/interview_gateway.py` -> `backend/modules/interview/websocket/interview_gateway.py`
- `backend/sockets/metrics.py` -> `backend/modules/analytics/websocket/metrics_socket.py`
- `backend/sessions/interview_session.py` -> `backend/modules/interview/sessions/interview_session.py`
- `backend/sessions/registry.py` -> `backend/modules/interview/sessions/registry.py`
- `backend/api/routes/candidate_routes.py` -> split route + schemas + service under `backend/modules/candidate/`
- `backend/api/routes/recruiter_dashboard_routes.py` -> `backend/modules/recruiter/routes/recruiter_routes.py`
- `backend/api/routes/resume_routes.py` -> `backend/modules/candidate/routes/resume_routes.py`
- `backend/api/routes/auth_routes.py` -> `backend/modules/recruiter/routes/auth_routes.py` (or shared auth routes)

### DELETE
- Root temp/debug artifacts:
  - `fix_*.py`, `re_fix_tests.py`, `test_import.py`, `test_conftest.py`
  - `out*.txt`, `err.txt`, `error.txt`, `pytest_*.txt`, `test_report*.txt`
  - `test_ws_interview.db`, `test_ws_metrics.db`
- Generated/cache directories:
  - `backend/**/__pycache__/`
  - `tests/__pycache__/`
- Non-source local environment/dependency directories accidentally committed:
  - `myenv/`
  - `node_modules/`
- `frontend/src/abandoned-status.css`
- Generated media in source tree:
  - `backend/static/audio/*.wav`

### DEPRECATE
- `backend/api/routes/recruiter_dashboard_routes.py` (if router moves to modules path)
- `backend/services/resume_parser_service.py` (retain as compatibility shim)
- `backend/core/code_engine.py` (not referenced)
- `backend/core/emotion_ai.py` (not referenced)
- `backend/services/audit_service.py` (not wired)
- `backend/services/telemetry_service.py` (not wired)

## Architectural Gaps vs Target Structure

- Missing: `backend/modules/*` domainized directory boundaries for candidate/recruiter/interview/evaluation/analytics.
- Missing: `backend/core/{config,logging,security,exceptions}` layering.
- Missing: `backend/infrastructure/{database,redis,storage,external_providers}` split.
- Current coupling hotspots:
  - `backend/main.py` (startup + middleware + many feature endpoints)
  - `backend/api/routes/candidate_routes.py` (schemas + business logic + route handlers)
  - `backend/sockets/interview_gateway.py` (ws protocol + orchestration + persistence concerns)

## Pass Execution Plan

1. Repository hygiene cleanup (delete temp/generated/noise files).
2. Introduce target folder scaffolding and move core/infrastructure modules with compatibility shims.
3. Route architecture refactor:
   - move recruiter router into modular path
   - include router from app
   - remove duplicate endpoints from `main.py`
4. Candidate route split into `schemas.py`, `services.py`, `routes.py`.
5. Interview module moves (`sessions`, `websocket`) with compatibility exports.
6. Dependency and config cleanup pass.
