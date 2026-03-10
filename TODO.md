# TODO: Remove Duplicate Files and Logic

## Phase 1: Remove Exact Duplicate Files (COMPLETED)

- [x] 1.1 Delete `backend/auth/routes.py` (keep `backend/api/routes/auth_routes.py`)
- [x] 1.2 Delete `backend/routes/candidate_routes.py` (keep `backend/api/routes/candidate_routes.py`)
- [x] 1.3 Delete `backend/routes/resume_routes.py` (keep `backend/api/routes/resume_routes.py`)

## Phase 2: Fix Internal Duplicates Within Files (COMPLETED)

- [x] 2.1 Fix `backend/api/routes/auth_routes.py` - Remove duplicated auth routes content (appears twice in file)
- [x] 2.2 Fix `backend/api/routes/resume_routes.py` - Remove duplicated upload_resume function (appears twice in file)

## Phase 3: Remove Duplicate get_db() Helper (COMPLETED)

- [x] 3.1 Remove get_db() from `backend/api/routes/candidate_routes.py` (already in database.py)

## Phase 4: Review Interview Architecture (Future)

- [ ] 4.1 Review `sockets/interview.py` vs `sockets/interview_gateway.py` for consolidation
- [ ] 4.2 Review dashboard models duplication between recruiter_dashboard.py and recruiter_dashboard_models.py

