# Intervux AI Remediation and Release Qualification Plan

Baseline: `ui-refactor` at `8e1f9f24969a9b87495d056520d9b4474860707b`
Remediation branch: `remediation/phase1-security`

This plan tracks the audit remediation in dependency order. A finding is marked
verified only when its stated check has been executed successfully. Passing
tests do not establish production deployment safety by themselves.

## Phase 1 — Security containment

| Item | Status | Acceptance evidence |
|---|---|---|
| Remove Compose database and Flower credential defaults | Complete | Compose requires `POSTGRES_PASSWORD` and `FLOWER_BASIC_AUTH`; the example leaves them blank. `docker-compose --env-file .env.docker config --quiet` succeeds with configured local values and rejects the blank example. |
| Protect resume uploads and downloads | Complete | Legacy parser upload requires a candidate identity. Stored resumes use an authenticated API route, restricted to the candidate owner or an admin. The public `/uploads` static mount was removed. Four focused access tests pass. |
| Enforce recruiter interview assignment checks | Complete | Recruiter interview reports, analytics, and decision summaries check the assigned job post owner; recruiter lists, comparisons, and dashboard aggregates are scoped to owned job posts. Unassigned viewers are denied. Five focused policy/database tests pass. |
| Enforce mock-interview WebSocket ownership | Complete | The gateway requires the runtime and mock-interview IDs to agree, checks the `mock-<32 lowercase hex>` format, and verifies candidate ownership and `in_progress` status before session registration or state hydration. Cross-candidate, recruiter/viewer, invalid-ID, lifecycle, and database-failure regression cases are covered in `tests/test_websocket_interview.py`. |

### Phase 1 verification

- `pytest -q tests/test_recruiter_access.py tests/test_resume_access.py` — **9 passed**.
- `pytest -q tests/test_resume_access.py tests/test_recruiter_access.py tests/test_websocket_interview.py tests/test_websocket_metrics.py` — **109 passed**, one warning.
- `pytest -q tests backend/tests` — **220 passed**, one warning, exit 0 (checkpoint verification).
- `pytest -q tests/test_websocket_metrics.py::TestMetricsWebSocketAuth::test_authentication_token_is_not_logged` — **1 passed**.
- `docker-compose --env-file .env.docker config --quiet` — **passed** with the local configured environment.
- `docker-compose --env-file .env.docker.example config --quiet` — **failed closed** because required Flower credentials are blank.
- `npx eslint src/pages/CandidateProfile.tsx` — **passed**.
- `git diff --check` — **passed**.

### Phase 1 limitations

- Candidate resume access is owner/admin only. Recruiter resume preview requires an explicit assignment-to-candidate identity mapping before it can be enabled safely.
- Viewer access is denied because the repository has no viewer assignment model.
- Deployment-level reachability and secret rotation were not assessed.

## Phase 2 — Reliable test baseline and credential-safe logging

| Item | Status | Acceptance evidence |
|---|---|---|
| Reproduce the four failures and two teardown errors individually | Complete | All six tests pass when run individually. |
| Diagnose and repair test database lifecycle/order behavior | Partially complete | All six prior failures/errors pass individually; the complete suite passes twice after remediation. The original suite-only failure was not reproduced and its cause remains unverified. |
| Investigate malformed JSON flood separately | Complete | `TestWebSocketStress.test_malformed_json_flood_stays_recoverable` passes individually and in the full suite. |
| Remove metrics WebSocket token logging | Complete | Auth log includes environment metadata only. Added regression test confirms the token is absent from captured logs. |
| Complete backend test suite | Passed | The earlier `pytest -q` run reported **193 passed**. The checkpoint run explicitly included both test roots: `pytest -q tests backend/tests` — **220 passed**, one warning, exit 0. |

## Phase 3 — Architecture and CI stabilization

Status: **Pending**

1. Identify and document the authoritative interview session state and
   persistence path. Explain how the active gateway/session registry relates to
   the domain aggregate and repository interfaces; implement no additional
   architecture until the boundary is agreed.
2. Add frontend lint, build, and test execution to CI. First make the frontend
   checks pass without broad cleanup. Current baseline: `npm run build` fails
   with existing TypeScript errors across unrelated files; `npm run lint`
   reports 122 existing errors and one warning. The changed resume page passes
   targeted ESLint.
3. Reconcile setup and architecture documentation with the actual Compose
   environment file and active runtime paths.

Exit criteria: architecture ownership is explicit; backend and frontend gates
run automatically; the required CI checks pass from a clean checkout.

## Phase 4 — Release qualification

Status: **Pending**

### Long-running session stability

- Define a representative interview workload, duration, concurrency, memory
  ceiling, cleanup interval, and recovery thresholds.
- Exercise repeated audio messages, reconnects, cancellations, model failures,
  and recovery.
- Record process memory, task/session counts, latency, and cleanup evidence.

### Replay equivalence

- Define a captured operation/event format and the state transitions and
  side-effects that must match exactly.
- Define acceptable variation for model-generated responses.
- Replay the same sequence more than once and compare state, event order, and
  durable side effects.

### Golden architecture snapshot

- Approve a stable snapshot of API/schema/configuration contracts and module
  dependency boundaries.
- Ensure intentional contract changes are reviewable and baseline updates are
  explicit.
- Avoid snapshots of generated or implementation-specific details.

### Deployment and AI qualification

- Verify production configuration, migration ordering, rollback procedures,
  health checks, and least-privilege service access.
- Qualify prompt-injection handling, output validation, provider failures,
  latency/token budgets, and evaluation quality against approved fixtures.

Exit criteria: all three stability checks meet approved measurable thresholds;
deployment and rollback evidence is reviewed; unresolved risks have explicit
owners and acceptance; a release go/no-go is recorded.

## Overall Definition of Done

- All Phase 1 controls remain in place and their negative authorization tests
  pass.
- The complete backend suite and required frontend CI checks pass repeatedly
  from a clean checkout.
- Interview persistence, assignment boundaries, configuration contracts, and
  operational procedures match the implementation.
- Long-session, replay, architecture snapshot, deployment, and AI qualification
  evidence is recorded and reviewed.
- Remaining risks are documented and explicitly accepted before release.
