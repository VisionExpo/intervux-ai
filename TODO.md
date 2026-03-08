# Implementation Plan

## Phase 1: Dashboard Updates
- [x] Update CandidateDashboard.tsx - Add "Welcome {name}" message
- [x] Add resume status indicator (✔/✗)
- [x] Show "Mock interviews remaining: X"

## Phase 2: Resume Upload
- [x] Add file upload component to CandidateProfile.tsx
- [x] Call POST /api/candidate/resume endpoint
- [x] Display parsed skills after upload

## Phase 3: Interview Report Page
- [x] Create new /report page for candidates
- [x] Display scores: Overall, Technical, Communication, Reasoning
- [x] Show strengths and improvements

## Phase 4: Mock Interview Limit Handling
- [x] Add limit check in MockInterview.tsx
- [x] Show appropriate message when 0 remaining
- [x] Disable start button when limit reached

## Phase 5: Route Updates
- [x] Add /report route to App.tsx
- [x] Ensure navigation to report after interview completion

