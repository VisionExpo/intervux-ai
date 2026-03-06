from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateInterviewReport,
    InterviewSummary,
    QuestionBreakdown,
    ReplayEvaluation,
    ReplaySegment,
    SkillAnalytics,
)
from backend.models.recruiter_dashboard_models import (
    Candidate,
    Interview,
    InterviewQuestion,
    InterviewReplaySegment,
)


def list_candidates(
    db: Session,
    page: int = 1,
    limit: int = 20,
    role: str | None = None,
    search: str | None = None,
) -> list[dict]:
    safe_page = max(page, 1)
    safe_limit = max(1, min(limit, 100))
    offset = (safe_page - 1) * safe_limit

    interview_rows = db.query(Interview.candidate_id, Interview.id).all()
    interview_ids = {candidate_id: interview_id for candidate_id, interview_id in interview_rows}
    query = db.query(Candidate)

    if role:
        query = query.filter(Candidate.role == role)

    if search:
        like_pattern = f"%{search.strip()}%"
        query = query.filter(
            Candidate.name.ilike(like_pattern)
            | Candidate.email.ilike(like_pattern)
            | Candidate.role.ilike(like_pattern)
        )

    candidates = query.order_by(Candidate.created_at.desc()).offset(offset).limit(safe_limit).all()
    return [
        {
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "role": candidate.role,
            "resume_url": candidate.resume_url or "",
            "created_at": candidate.created_at,
            "interview_id": interview_ids.get(candidate.id),
        }
        for candidate in candidates
    ]


def get_candidates(
    db: Session,
    page: int = 1,
    limit: int = 20,
    role: str | None = None,
    search: str | None = None,
) -> list[dict]:
    return list_candidates(db, page=page, limit=limit, role=role, search=search)


def get_interview_report(db: Session, interview_id: str) -> CandidateInterviewReport:
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    questions = (
        db.query(InterviewQuestion)
        .filter(InterviewQuestion.interview_id == interview_id)
        .order_by(InterviewQuestion.id.asc())
        .all()
    )
    replay_segments = (
        db.query(InterviewReplaySegment)
        .filter(InterviewReplaySegment.interview_id == interview_id)
        .order_by(InterviewReplaySegment.created_at.asc())
        .all()
    )

    return CandidateInterviewReport(
        candidate={
            "id": candidate.id,
            "name": candidate.name,
            "email": candidate.email,
            "role": candidate.role,
            "resume_url": candidate.resume_url or "",
            "created_at": candidate.created_at,
        },
        interview=InterviewSummary(
            id=interview.id,
            candidate_id=interview.candidate_id,
            role=interview.role,
            overall_score=interview.overall_score or 0.0,
            technical_score=interview.technical_score or 0.0,
            communication_score=interview.communication_score or 0.0,
            problem_solving_score=interview.problem_solving_score or 0.0,
            started_at=interview.started_at or candidate.created_at,
            completed_at=interview.completed_at or interview.started_at or candidate.created_at,
        ),
        questions=[
            QuestionBreakdown(
                id=question.id,
                interview_id=question.interview_id,
                question=question.question,
                answer=question.answer or "",
                score=question.score or 0.0,
                feedback=question.feedback or "",
            )
            for question in questions
        ],
        replay_segments=[
            ReplaySegment(
                question=segment.question,
                candidate_audio=segment.audio_url or "",
                transcript=segment.transcript or "",
                evaluation=ReplayEvaluation(
                    technical=segment.score or 0.0,
                    clarity=segment.score or 0.0,
                    reasoning=segment.score or 0.0,
                ),
            )
            for segment in replay_segments
        ],
    )


def get_interview(db: Session, interview_id: str) -> Interview | None:
    return db.query(Interview).filter(Interview.id == interview_id).first()


def get_skill_analytics(db: Session, interview_id: str) -> SkillAnalytics:
    interview = get_interview(db, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    analytics = (
        db.query(
            func.avg(InterviewQuestion.score).label("avg_score"),
            func.count(InterviewQuestion.id).label("questions"),
            func.max(InterviewQuestion.score).label("best_score"),
            func.min(InterviewQuestion.score).label("lowest_score"),
        )
        .filter(InterviewQuestion.interview_id == interview_id)
        .first()
    )

    avg_score = float(analytics.avg_score) if analytics and analytics.avg_score is not None else 0.0
    question_count = int(analytics.questions) if analytics else 0
    best_score = float(analytics.best_score) if analytics and analytics.best_score is not None else 0.0
    lowest_score = float(analytics.lowest_score) if analytics and analytics.lowest_score is not None else 0.0

    return SkillAnalytics(
        interview_id=interview_id,
        skills={
            "avg_score": avg_score,
            "questions": float(question_count),
            "best_question": best_score,
            "lowest_question": lowest_score,
            "technical": interview.technical_score or 0.0,
            "communication": interview.communication_score or 0.0,
            "problem_solving": interview.problem_solving_score or 0.0,
            "overall": interview.overall_score or 0.0,
        },
    )


def get_interview_analytics(db: Session, interview_id: str) -> SkillAnalytics:
    return get_skill_analytics(db, interview_id)


def compare_candidates(db: Session) -> list[CandidateComparisonRow]:
    rows = (
        db.query(
            Candidate.id.label("candidate_id"),
            Candidate.name.label("candidate_name"),
            Interview.technical_score.label("technical"),
            Interview.communication_score.label("communication"),
            Interview.overall_score.label("overall"),
        )
        .join(Interview, Candidate.id == Interview.candidate_id)
        .order_by(Interview.overall_score.desc())
        .all()
    )
    return [
        CandidateComparisonRow(
            candidate_id=row.candidate_id,
            candidate_name=row.candidate_name,
            technical=row.technical or 0.0,
            communication=row.communication or 0.0,
            overall=row.overall or 0.0,
        )
        for row in rows
    ]
