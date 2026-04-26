import asyncio
import base64
import json
import os
import uuid
import sys
from pathlib import Path

# Ensure absolute imports like `from backend...` work
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database.database import AsyncSessionLocal
from backend.models.recruiter_dashboard_models import JobPost, Candidate, Interview, JobPostStatus, CandidateStatus
from backend.core.security.jwt_service import create_access_token
import websockets

async def create_test_data():
    async with AsyncSessionLocal() as db:
        # 1. Create JobPost
        job_post = JobPost(
            id=str(uuid.uuid4()),
            title="Senior Python Engineer",
            description="A role for testing resume parsing and interview flow.",
            recruiter_id="recruiter-001",
            status=JobPostStatus.ACTIVE.value,
            ai_interview_enabled="true"
        )
        db.add(job_post)
        await db.flush()
        
        # 2. Create Candidate
        candidate = Candidate(
            id=str(uuid.uuid4()),
            name="Vishal Gorule",
            email=f"vishal.{uuid.uuid4().hex[:6]}@example.com",
            role="Software Engineer",
            job_post_id=job_post.id,
            status=CandidateStatus.INVITED.value
        )
        db.add(candidate)
        await db.flush()
        
        # 3. Create Interview
        interview = Interview(
            id=str(uuid.uuid4()),
            candidate_id=candidate.id,
            role="Software Engineer"
        )
        db.add(interview)
        await db.flush()
        
        await db.commit()
        print(f"[INFO] Created Test Data:")
        print(f"  - JobPost ID: {job_post.id}")
        print(f"  - Candidate ID: {candidate.id}")
        print(f"  - Interview ID: {interview.id}")
        
        return interview.id

def generate_token():
    user_data = {
        "user_id": "recruiter-001",
        "email": "recruiter@intervux.ai",
        "name": "Recruiter User",
        "role": "recruiter"
    }
    token = create_access_token(user_data)
    return token

async def test_resume_upload(interview_id, token):
    uri = f"ws://localhost:8000/ws/interview?token={token}&session_id={interview_id}"
    
    resume_path = project_root / "sample_resume.pdf"
    if not resume_path.exists():
        print(f"[ERROR] {resume_path} not found!")
        return

    with open(resume_path, "rb") as f:
        resume_bytes = f.read()
    
    resume_b64 = base64.b64encode(resume_bytes).decode("utf-8")
    
    print(f"[INFO] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("[INFO] Connected! Waiting for greeting...")
            
            # 1. Receive Greeting
            while True:
                resp = await websocket.recv()
                if isinstance(resp, str):
                    data = json.loads(resp)
                    print(f"[WS RECV] {data.get('type')}: {data.get('text', '')[:100]}...")
                    if data.get("type") == "PHASE_CHANGE" and data.get("phase") == "waiting_resume":
                        break
                else:
                    print(f"[WS RECV] Bytes chunk received")

            print("[INFO] Sending resume_upload message...")
            # 2. Send Resume
            upload_msg = {
                "type": "resume_upload",
                "file_name": "sample_resume.pdf",
                "file_bytes": resume_b64,
                "version": "v1"
            }
            await websocket.send(json.dumps(upload_msg))
            
            print("[INFO] Resume message SENT. Waiting for processing...")

            # 3. Wait for question
            start_time = time.time()
            while True:
                try:
                    resp = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    if isinstance(resp, str):
                        data = json.loads(resp)
                        m_type = data.get("type")
                        print(f"[WS RECV] {m_type}")
                        if m_type == "avatar_sync":
                            print(f"[SUCCESS] Received initial question: {data.get('text')}")
                            return True
                        if m_type == "PHASE_CHANGE":
                            print(f"[PHASE] -> {data.get('phase')}")
                        if m_type == "ERROR":
                            print(f"[ERROR] Received error: {data.get('message')}")
                            return False
                    else:
                        print("[WS RECV] Binary data received")
                except asyncio.TimeoutError:
                    elapsed = time.time() - start_time
                    print(f"[INFO] Still waiting... ({int(elapsed)}s elapsed)")
                    # Heartbeat
                    await websocket.send(json.dumps({"type": "ping"}))
                    if elapsed > 100:
                        print("[FAIL] Test timed out waiting for processing.")
                        return False
            
    except Exception as e:
        print(f"[ERROR] WebSocket failed: {e}")
        return False

async def main():
    try:
        interview_id = await create_test_data()
        token = generate_token()
        success = await test_resume_upload(interview_id, token)
        if success:
            print("\n" + "="*40)
            print("✨ E2E RESUME UPLOAD TEST PASSED! ✨")
            print("="*40)
            sys.exit(0)
        else:
            print("\n" + "="*40)
            print("❌ E2E RESUME UPLOAD TEST FAILED! ❌")
            print("="*40)
            sys.exit(1)
    except Exception as e:
        print(f"[CRITICAL] Test aborted: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
