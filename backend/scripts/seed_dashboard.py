from __future__ import annotations

import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.db.database import Base, AsyncSessionLocal, engine
from sqlalchemy import select
from backend.models import recruiter_dashboard_models  # noqa: F401
from backend.models.recruiter_dashboard_models import (
    Candidate,
    Interview,
    InterviewQuestion,
    InterviewReplaySegment,
)


async def seed_dashboard() -> None:
    # Using run_sync to create tables in async environment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Candidate))
        if len(res.all()) > 0:
            print("Dashboard seed skipped: candidates already exist.")
            return

        now = datetime.utcnow()

        candidates = [
            Candidate(
                id=str(uuid.uuid4()),
                name="John Doe",
                email="john@example.com",
                role="ML Engineer",
                resume_url="resume-john.pdf",
                created_at=now - timedelta(days=3),
            ),
            Candidate(
                id=str(uuid.uuid4()),
                name="Priya Nair",
                email="priya@example.com",
                role="Backend Engineer",
                resume_url="resume-priya.pdf",
                created_at=now - timedelta(days=2),
            ),
            Candidate(
                id=str(uuid.uuid4()),
                name="Arjun Patel",
                email="arjun@example.com",
                role="Python Engineer",
                resume_url="resume-arjun.pdf",
                created_at=now - timedelta(days=1),
            ),
        ]
        db.add_all(candidates)
        await db.flush()

        interviews = [
            Interview(
                id=str(uuid.uuid4()),
                candidate_id=candidates[0].id,
                role=candidates[0].role,
                overall_score=87.0,
                technical_score=89.0,
                communication_score=84.0,
                problem_solving_score=86.0,
                started_at=now - timedelta(days=2, minutes=50),
                completed_at=now - timedelta(days=2, minutes=5),
            ),
            Interview(
                id=str(uuid.uuid4()),
                candidate_id=candidates[1].id,
                role=candidates[1].role,
                overall_score=79.0,
                technical_score=81.0,
                communication_score=77.0,
                problem_solving_score=78.0,
                started_at=now - timedelta(days=1, minutes=45),
                completed_at=now - timedelta(days=1, minutes=3),
            ),
            Interview(
                id=str(uuid.uuid4()),
                candidate_id=candidates[2].id,
                role=candidates[2].role,
                overall_score=91.0,
                technical_score=93.0,
                communication_score=88.0,
                problem_solving_score=92.0,
                started_at=now - timedelta(hours=20),
                completed_at=now - timedelta(hours=19, minutes=18),
            ),
        ]
        db.add_all(interviews)
        await db.flush()

        questions = [
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[0].id,
                question="How would you evaluate model drift in production?",
                answer="Track feature drift, label drift, and business KPI regression.",
                score=8.8,
                feedback="Strong production awareness.",
            ),
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[0].id,
                question="Explain precision-recall tradeoffs.",
                answer="Optimize based on false positive versus false negative cost.",
                score=8.5,
                feedback="Clear and practical framing.",
            ),
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[1].id,
                question="How do you debug a slow query?",
                answer="Start with the execution plan, indexes, and lock contention.",
                score=7.9,
                feedback="Solid debugging path.",
            ),
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[1].id,
                question="Explain idempotency in APIs.",
                answer="Repeated requests should not create duplicate side effects.",
                score=7.7,
                feedback="Correct, but could use stronger examples.",
            ),
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[2].id,
                question="What are Python generators used for?",
                answer="Lazy iteration, streaming, and memory-efficient pipelines.",
                score=9.2,
                feedback="Clear and concise.",
            ),
            InterviewQuestion(
                id=str(uuid.uuid4()),
                interview_id=interviews[2].id,
                question="Design a scalable task queue.",
                answer="Use durable queues, retries, dead-letter queues, and worker autoscaling.",
                score=9.0,
                feedback="Strong systems thinking.",
            ),
        ]
        db.add_all(questions)

        replay_segments = [
            InterviewReplaySegment(
                id=str(uuid.uuid4()),
                interview_id=interviews[0].id,
                question="How would you evaluate model drift in production?",
                transcript="I would compare live distributions against the training baseline and watch business metrics.",
                audio_url="https://example.com/audio/john-drift.wav",
                score=8.8,
                created_at=interviews[0].started_at + timedelta(minutes=10),
            ),
            InterviewReplaySegment(
                id=str(uuid.uuid4()),
                interview_id=interviews[1].id,
                question="How do you debug a slow query?",
                transcript="I would inspect the query plan, table stats, and lock waits first.",
                audio_url="https://example.com/audio/priya-query.wav",
                score=7.9,
                created_at=interviews[1].started_at + timedelta(minutes=12),
            ),
            InterviewReplaySegment(
                id=str(uuid.uuid4()),
                interview_id=interviews[2].id,
                question="Design a scalable task queue.",
                transcript="I would separate enqueueing from workers, add retries, and monitor queue lag.",
                audio_url="https://example.com/audio/arjun-queue.wav",
                score=9.0,
                created_at=interviews[2].started_at + timedelta(minutes=15),
            ),
        ]
        db.add_all(replay_segments)

        await db.commit()
        print("Dashboard seed completed.")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_dashboard())
