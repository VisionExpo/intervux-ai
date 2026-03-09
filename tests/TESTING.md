# TESTING.md

# Intervux AI – Testing Guide

This document describes how to test the Intervux AI platform locally.
The goal is to verify that all core systems work correctly:

* Authentication
* Resume parsing
* WebSocket interview engine
* Audio streaming
* AI question generation
* Evaluation pipeline
* Interview UI
* Reporting system

Testing should always be performed **layer-by-layer**, starting from the backend and ending with a full end-to-end interview.

---

# 1. Environment Setup

## Requirements

* Python 3.10+
* Node.js 18+
* npm or pnpm
* Chrome / Edge browser (recommended for WebRTC)

## Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

# 2. Start the System

## Start Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend should start at:

```
http://localhost:8000
```

Swagger docs:

```
http://localhost:8000/docs
```

---

## Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

# 3. Backend API Testing

## 3.1 Authentication

Test login endpoint using Swagger or curl.

```
POST /auth/login
```

Example request:

```json
{
  "email": "candidate@test.com",
  "password": "password123"
}
```

Expected response:

```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

---

## 3.2 Resume Upload

Endpoint:

```
POST /candidate/resume
```

Upload a PDF or DOCX resume.

Expected behavior:

* Resume stored
* Skills extracted
* Candidate profile updated

Backend logs should show:

```
Resume parsed successfully
Skills extracted
```

---

# 4. WebSocket Interview Engine Testing

Test the WebSocket independently before using the UI.

Open browser console:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/interview?token=YOUR_TOKEN")

ws.onmessage = (event) => {
  console.log("Message:", event.data)
}
```

Start interview:

```javascript
ws.send(JSON.stringify({
  type: "start_interview"
}))
```

Expected response:

```
greeting
question
```

Backend logs:

```
connection open
Interview session started
Question generated
```

---

# 5. Resume Context Verification

Ensure the AI interview uses resume information.

Test case:

1. Upload resume
2. Start interview

Expected AI question example:

```
I see you built an MLOps platform for stock forecasting.
Can you explain how you handled model versioning?
```

If resume context is not used, verify:

* resume parser output
* context injection into interview engine

---

# 6. Frontend WebSocket Testing

Inside the browser console, verify WebSocket events.

Expected console logs:

```
WebSocket connected successfully
WebSocket message received
WebSocket message received
```

If you see:

```
WebSocket closed
WebSocket reconnecting
```

then the frontend is reconnecting incorrectly.

Check `useInterview.ts`.

---

# 7. Interview UI Component Testing

Each component should be tested individually.

---

## Resume Upload Panel

Expected behavior:

* File selection works
* Resume name displayed
* Start Interview button enabled

---

## Start Interview Button

Click once.

Expected behavior:

```
WebSocket start_interview message sent
```

Verify it is **not triggered multiple times**.

---

## Transcript Panel

Expected output format:

```
AI Interviewer
Question text

Candidate
Answer transcript
```

Messages should not duplicate.

---

## Coding Sandbox

Verify Monaco editor loads correctly.

Expected features:

* language selection
* code editing
* run button
* output panel

---

## Candidate Camera

Expected behavior:

Browser prompts for permission.

```
Allow camera access?
```

After approval:

```
Live video preview appears
```

If camera remains stuck at:

```
Initializing camera...
```

Check browser permissions.

---

# 8. Audio Streaming Test

Verify microphone audio is captured and sent.

Expected logs:

```
Audio stream started
Audio chunk sent
Audio chunk sent
```

Backend should receive audio packets.

---

# 9. Evaluation Pipeline Test

Verify that candidate answers trigger evaluation.

Backend logs should show:

```
Transcript received
Evaluating answer
Score generated
Next question created
```

---

# 10. Interview Completion Test

Run a full interview session.

Expected flow:

```
AI greeting
↓
Question 1
↓
Candidate answer
↓
Evaluation
↓
Next question
↓
Interview complete
↓
Report page generated
```

---

# 11. Interview Report Testing

After interview completion, navigate to:

```
/report
```

Expected report elements:

* overall score
* technical score
* communication score
* reasoning score
* strengths
* improvement areas

---

# 12. Debug Logging

During development enable debug logs.

Backend:

```
Interview started
Question generated
Answer received
Evaluation complete
```

Frontend:

```
WebSocket connected
Start interview triggered
Message received
```

These logs help isolate system issues quickly.

---

# 13. Known Issues Checklist

When debugging, verify the following:

```
[ ] Backend server running
[ ] Frontend server running
[ ] JWT token valid
[ ] Resume uploaded successfully
[ ] WebSocket connection established
[ ] start_interview sent once
[ ] AI greeting received
[ ] Questions generated
[ ] Audio streaming working
[ ] Transcript updating
[ ] Report generated
```

---

# 14. End-to-End Demo Test

Final test scenario:

```
1. Login as candidate
2. Upload resume
3. Start mock interview
4. AI asks questions
5. Candidate answers verbally
6. Evaluation occurs
7. Interview ends
8. Report displayed
```

If all steps pass, **Intervux AI v1 demo is working correctly.**

---

# 15. Future Automated Testing (Planned)

Future improvements may include:

* API unit tests
* WebSocket integration tests
* resume parser tests
* UI component tests
* load testing for interview sessions
