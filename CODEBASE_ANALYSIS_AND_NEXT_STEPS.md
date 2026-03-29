# Codebase Analysis and Next Steps

_Last updated: 2026-03-29_

## Executive Summary

Intervux AI already has a strong full-stack baseline: FastAPI + WebSocket interview runtime, React candidate/recruiter UI, candidate auth flows, and an established test suite (`173` tests discovered). The highest near-term opportunity is to improve delivery confidence by stabilizing the automated test pipeline, then focus on production-readiness hardening and frontend routing consistency.

Recent progress: the LLM fallback system is now hardened to fail over on provider availability/configuration failures (not only quota scenarios), with dedicated unit coverage.

## Current Snapshot

### Architecture & Stack

- **Backend**: FastAPI app with REST + WebSocket, SQLAlchemy models, auth, and dashboard/candidate route modules.
- **Interview Runtime**: `InterviewGateway` + session/engine architecture supports live interview interactions.
- **Frontend**: React + Vite + TypeScript with role-based UX and hash-route navigation.
- **Infra support**: Docker Compose includes Postgres, Redis, worker, Flower.

### Repository Signals

- Python is still the dominant code surface, followed by TS/TSX.
- Architecture docs and flow docs are present and useful (`ARCHITECTURE.md`, `SYSTEM_FLOW.md`).
- A frontend enhancement backlog exists and appears partially completed (`frontend/TODO_ENHANCEMENTS.md`).

## Key Findings

1. **Immediate CI blocker in test suite (fixed in this change)**
   - `tests/test_websocket_interview.py` had non-UTF-8 bytes (`0x97`) causing `pytest` collection failure.
   - This prevented the entire suite from executing, masking deeper quality signal.

2. **Frontend routing consistency risk**
   - The app uses hash routing (`window.location.hash`) in `App.tsx`.
   - `authFetch` currently redirects unauthorized users with `window.location.href = "/login"`, which can conflict with hash-based routing behavior.

3. **Security headers are present but CSP is strict/static**
   - Backend injects security headers globally.
   - Current CSP may need environment-aware tuning for production assets (analytics, font/CDN allowances if introduced later).

4. **Operational readiness is improving but not yet fully proven**
   - Health/readiness endpoints and runtime monitoring exist.
   - Need explicit reliability checks in CI for async/websocket paths and worker queues.

## Recommended Next Steps (Prioritized)

### Phase 1 (This sprint): Reliability and developer velocity

1. **Keep tests always collectable**
   - Add a pre-commit or CI guard to reject non-UTF-8 source/test files.
2. **Turn current `pytest` run into a CI gate**
   - Ensure full suite executes on each PR and branch push.
   - Status: Implemented via GitHub Actions workflow `.github/workflows/tests.yml` (`CI Gate` / `test-gate (python-3.10)`).
   - Branch protection: mark this status check as **required** on protected branches.
3. **Document local runbook**
   - Add a short "dev quickstart + common failures" section to README.

### Phase 2 (Next sprint): Frontend correctness and UX consistency

4. **Unify routing behavior**
   - Standardize unauthorized navigation to hash route (`#/login`) or migrate to a formal router (`react-router-dom`) and remove custom hash switch logic.
5. **Close interviewer panel validation loop**
   - Complete Step 4 from `frontend/TODO_ENHANCEMENTS.md` with explicit acceptance criteria and lightweight integration tests.

### Phase 3 (2-4 weeks): Production hardening

6. **Strengthen WebSocket resilience tests**
   - Add tests for reconnect behavior, malformed frames, and prolonged session handling.
   - Status: Partially implemented in `tests/test_websocket_interview.py` (`TestWebSocketStress`) with rapid reconnect and malformed JSON flood coverage.
7. **Improve observability SLOs**
   - Define SLO targets (e.g., interview turn latency, WS disconnect rate, evaluation completion rate) and alert thresholds.
8. **Resume parsing strategy consolidation**
   - Continue unifying resume parse paths behind one contract and measurable fallback behavior.

## Suggested Ownership Split

- **Backend owner**: test reliability, websocket resilience, parser unification.
- **Frontend owner**: routing consistency, interview flow polish, auth UX.
- **Platform owner**: CI quality gates, SLO dashboards/alerts.

## Acceptance Criteria for Next Milestone

- Full pytest suite collects and runs in CI.
- No route mismatch between auth errors and candidate/recruiter navigation.
- WebSocket interview flow has deterministic smoke test coverage.
- README includes up-to-date run/test/troubleshooting guidance.

