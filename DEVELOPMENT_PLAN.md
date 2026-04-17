# 🌳 Intervux AI: Master Development Plan

This document serves as the master hierarchical plan (structured as a tree) to fix all identified bugs, complete missing features, and fully modernize the Intervux AI platform.

## 1. 🐛 Bug Fixes & Stabilization (Immediate Priority)
*(Subplan targeting direct console and compilation errors)*

- **1.1. Frontend React/Linting Bugs**
  - **1.1.1.** *Bug:* `useAuth.tsx` contains both components (`AuthProvider`) and regular functions (`useAuth`, `authFetch`). This breaks Vite's Fast Refresh.
    - *Fix:* Split into `AuthContext.tsx` (context & hooks) and `authFetch.ts` (utility).
  - **1.1.2.** *Bug:* Missing dependencies in `useEffect` within `useInterview.ts`.
    - *Fix:* Add `connectSocket` or restructure the hook to properly memoize the websocket connection.
  - **1.1.3.** *Bug:* `Unexpected any` in `useDashboardApi.ts`.
    - *Fix:* Define proper TypeScript request/response interfaces for the API fetches.
- **1.2. Backend Environment & Testing**
  - **1.2.1.** *Bug:* Tests cannot run because `pytest` and test dependencies aren't globally accessible or properly synced to the active `venv`.
    - *Fix:* Centralize dependency management (e.g., standardizing `requirements/base.txt` vs `requirements/test.txt`), and implement automated script to run `pytest` via `venv`.
  - **1.2.2.** *Bug:* Users running global `uvicorn` encounter missing packages (like `asyncpg`).
    - *Fix:* Add a reliable `start.bat` / `start.sh` script that enforces `venv` activation before booting `uvicorn`.

## 2. 🏗️ Frontend UI Modernization (Architecture Implementation)
*(Subplan targeting the transition from Tailwind to a Premium Vanilla CSS Module System)*

- **2.1. Phase 1: Core Design System & CSS Tokenization**
  - **2.1.1.** Create `styles/tokens.css` with Deep Ocean Blue / Indigo variables (colors, blurs, spacing).
  - **2.1.2.** Create `styles/globals.css` and delete the monolithic `App.css`.
  - **2.1.3.** Eradicate remaining `Tailwind` utility classes across the application layouts to prevent specificity collisions.
- **2.2. Phase 2: Primitive Components Framework**
  - **2.2.1.** Build `<GlassCard>` with Vanilla CSS Modules to replace generic nested `div` panels.
  - **2.2.2.** Build shared `<Button>` with micro-animations & active glows.
  - **2.2.3.** Build shared `<AuthSurface>` layout component for `Login.tsx` and `Signup.tsx`.
- **2.3. Phase 3: Dashboard & Workflow Migration**
  - **2.3.1.** Migrate Candidate, Recruiter, and Admin dashboards to use the robust `<GlassCard>` arrays and centralized `<PageShell>`.
  - **2.3.2.** Replace ad-hoc tables with a standardized responsive `<DataTable>` component.

## 3. 🚀 Backend Missing Features & Hardening
*(Subplan targeting scale, edge cases, and robustness)*

- **3.1. Telemetry & Analytics**
  - **3.1.1.** Ensure `metrics_socket.py` broadcasts real-time LLM tracking to the Recruiter Dashboard successfully.
  - **3.1.2.** Standardize the `RuntimeMonitor` to dynamically scale or log warnings if TTS (Text-to-Speech) / Celery queues become blocked.
- **3.2. Database & State Integrity**
  - **3.2.1.** Replace fallback `create_all` SQLite behaviors with robust Alembic migrations enforced even in dev setups.
  - **3.2.2.** Validate Redis state cleanup when a websocket interview drops unexpectedly, preventing zombie candidate states.
