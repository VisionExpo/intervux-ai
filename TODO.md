# TODO - Candidate Portal v1

## Phase 1: Database & Auth Updates ✅

- [x] 1.1 Create database migration for candidate_profiles table
- [x] 1.2 Create database migration for mock_interviews table  
- [x] 1.3 Create database migration for notifications table
- [x] 1.4 Add CANDIDATE role to auth system
- [x] 1.5 Create candidate signup endpoint

## Phase 2: Backend APIs ✅

- [x] 2.1 Create candidate profile routes (GET/PUT)
- [x] 2.2 Create resume upload endpoint
- [x] 2.3 Create mock interview endpoints (start/history)
- [x] 2.4 Create notifications endpoint

## Phase 3: Frontend Pages ✅

- [x] 3.1 Create Signup page
- [x] 3.2 Update Login page with role selection
- [x] 3.3 Create Candidate Dashboard page
- [x] 3.4 Create Profile page
- [x] 3.5 Create Mock Interview page
- [x] 3.6 Create Interview History page
- [x] 3.7 Create Notifications page
- [x] 3.8 Update App.tsx routing for candidate portal

## Phase 4: Integration & Testing

- [ ] 4.1 Run database migrations
- [ ] 4.2 Test candidate signup flow
- [ ] 4.3 Test resume upload and parsing
- [ ] 4.4 Test mock interview flow
- [ ] 4.5 Test notifications

## Files Created/Modified

### Backend
- `alembic/versions/003_candidate_portal.py` - Database migration
- `backend/models/candidate_portal.py` - SQLAlchemy models
- `backend/routes/candidate_routes.py` - API routes
- `backend/auth/jwt_service.py` - Added CANDIDATE role
- `backend/main.py` - Registered candidate routes

### Frontend
- `frontend/src/pages/Signup.tsx` - New signup page
- `frontend/src/pages/CandidateDashboard.tsx` - Dashboard
- `frontend/src/pages/CandidateProfile.tsx` - Profile management
- `frontend/src/pages/MockInterview.tsx` - Mock interview
- `frontend/src/pages/InterviewHistory.tsx` - Interview history
- `frontend/src/pages/CandidateNotifications.tsx` - Notifications
- `frontend/src/App.tsx` - Routing
- `frontend/src/App.css` - Styles

