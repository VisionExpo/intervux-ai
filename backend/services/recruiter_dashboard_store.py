from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateCreate,
    CandidateInterviewReport,
    InterviewSummary,
    JobPost,
    JobPostCreate,
    JobPostUpdate,
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
    JobPost as JobPostModel,
    JobSkill as JobSkillModel,
    JobPostStatus,
    CandidateStatus,
    ExperienceLevel,
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


# =========================================================
# Job Post Functions
# =========================================================


def create_job_post(
    db: Session,
    job_data: JobPostCreate,
    created_by: str | None = None,
) -> JobPost:
    """Create a new job post with skills."""
    # Create job post
    db_job = JobPostModel(
        title=job_data.title,
        description=job_data.description,
        experience_level=job_data.experience_level,
        status=JobPostStatus.DRAFT.value,
        ai_interview_enabled="true" if job_data.ai_interview_enabled else "false",
        interview_limit=job_data.interview_limit,
        created_by=created_by,
    )
    db.add(db_job)
    db.flush()  # Get the ID

    # Add skills
    for skill_name in job_data.skills:
        db_skill = JobSkillModel(
            job_post_id=db_job.id,
            skill_name=skill_name,
            is_required="true",
        )
        db.add(db_skill)

    db.commit()
    db.refresh(db_job)

    # Fetch skills
    skills = db.query(JobSkillModel).filter(JobSkillModel.job_post_id == db_job.id).all()

    return JobPost(
        id=db_job.id,
        title=db_job.title,
        description=db_job.description,
        experience_level=db_job.experience_level,
        status=db_job.status,
        ai_interview_enabled=db_job.ai_interview_enabled == "true",
        interview_limit=db_job.interview_limit,
        created_at=db_job.created_at,
        updated_at=db_job.updated_at,
        created_by=db_job.created_by,
        skills=[
            JobSkill(
                id=skill.id,
                job_post_id=skill.job_post_id,
                skill_name=skill.skill_name,
                is_required=skill.is_required == "true",
                proficiency_level=skill.proficiency_level,
            )
            for skill in skills
        ],
    )


def list_job_posts(
    db: Session,
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
) -> list[JobPost]:
    """List all job posts."""
    safe_page = max(page, 1)
    safe_limit = max(1, min(limit, 100))
    offset = (safe_page - 1) * safe_limit

    query = db.query(JobPostModel)

    if status:
        query = query.filter(JobPostModel.status == status)

    job_posts = query.order_by(JobPostModel.created_at.desc()).offset(offset).limit(safe_limit).all()

    result = []
    for job in job_posts:
        skills = db.query(JobSkillModel).filter(JobSkillModel.job_post_id == job.id).all()
        result.append(
            JobPost(
                id=job.id,
                title=job.title,
                description=job.description,
                experience_level=job.experience_level,
                status=job.status,
                ai_interview_enabled=job.ai_interview_enabled == "true",
                interview_limit=job.interview_limit,
                created_at=job.created_at,
                updated_at=job.updated_at,
                created_by=job.created_by,
                skills=[
                    JobSkill(
                        id=skill.id,
                        job_post_id=skill.job_post_id,
                        skill_name=skill.skill_name,
                        is_required=skill.is_required == "true",
                        proficiency_level=skill.proficiency_level,
                    )
                    for skill in skills
                ],
            )
        )

    return result


def get_job_post(db: Session, job_post_id: str) -> JobPost | None:
    """Get a single job post by ID."""
    job = db.query(JobPostModel).filter(JobPostModel.id == job_post_id).first()
    if not job:
        return None

    skills = db.query(JobSkillModel).filter(JobSkillModel.job_post_id == job.id).all()

    return JobPost(
        id=job.id,
        title=job.title,
        description=job.description,
        experience_level=job.experience_level,
        status=job.status,
        ai_interview_enabled=job.ai_interview_enabled == "true",
        interview_limit=job.interview_limit,
        created_at=job.created_at,
        updated_at=job.updated_at,
        created_by=job.created_by,
        skills=[
            JobSkill(
                id=skill.id,
                job_post_id=skill.job_post_id,
                skill_name=skill.skill_name,
                is_required=skill.is_required == "true",
                proficiency_level=skill.proficiency_level,
            )
            for skill in skills
        ],
    )


def update_job_post(
    db: Session,
    job_post_id: str,
    job_data: JobPostUpdate,
) -> JobPost | None:
    """Update an existing job post."""
    job = db.query(JobPostModel).filter(JobPostModel.id == job_post_id).first()
    if not job:
        return None

    # Update fields
    if job_data.title is not None:
        job.title = job_data.title
    if job_data.description is not None:
        job.description = job_data.description
    if job_data.experience_level is not None:
        job.experience_level = job_data.experience_level
    if job_data.status is not None:
        job.status = job_data.status
    if job_data.ai_interview_enabled is not None:
        job.ai_interview_enabled = "true" if job_data.ai_interview_enabled else "false"
    if job_data.interview_limit is not None:
        job.interview_limit = job_data.interview_limit

    # Update skills if provided
    if job_data.skills is not None:
        # Delete existing skills
        db.query(JobSkillModel).filter(JobSkillModel.job_post_id == job.id).delete()
        # Add new skills
        for skill_name in job_data.skills:
            db_skill = JobSkillModel(
                job_post_id=job.id,
                skill_name=skill_name,
                is_required="true",
            )
            db.add(db_skill)

    db.commit()
    db.refresh(job)

    skills = db.query(JobSkillModel).filter(JobSkillModel.job_post_id == job.id).all()

    return JobPost(
        id=job.id,
        title=job.title,
        description=job.description,
        experience_level=job.experience_level,
        status=job.status,
        ai_interview_enabled=job.ai_interview_enabled == "true",
        interview_limit=job.interview_limit,
        created_at=job.created_at,
        updated_at=job.updated_at,
        created_by=job.created_by,
        skills=[
            JobSkill(
                id=skill.id,
                job_post_id=skill.job_post_id,
                skill_name=skill.skill_name,
                is_required=skill.is_required == "true",
                proficiency_level=skill.proficiency_level,
            )
            for skill in skills
        ],
    )


def delete_job_post(db: Session, job_post_id: str) -> bool:
    """Delete a job post and its skills."""
    job = db.query(JobPostModel).filter(JobPostModel.id == job_post_id).first()
    if not job:
        return False

    # Delete skills first
    db.query(JobSkillModel).filter(JobSkillModel.job_post_id == job_post_id).delete()
    # Delete job
    db.delete(job)
    db.commit()

    return True


def generate_interview_link(db: Session, candidate_id: str, expires_in_days: int = 7) -> tuple[str, datetime]:
    """Generate an expiring interview link for a candidate."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Generate unique token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    interview_link = f"/interview/{token}"
    candidate.interview_link = interview_link
    candidate.interview_link_expires_at = expires_at

    db.commit()

    return interview_link, expires_at


def invite_candidate(
    db: Session,
    candidate_data: CandidateCreate,
) -> Candidate:
    """Invite a candidate to a job post."""
    db_candidate = Candidate(
        name=candidate_data.name,
        email=candidate_data.email,
        role=candidate_data.role,
        job_post_id=candidate_data.job_post_id,
        resume_url=candidate_data.resume_url or "",
        status=CandidateStatus.INVITED.value,
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)

    return Candidate(
        id=db_candidate.id,
        name=db_candidate.name,
        email=db_candidate.email,
        role=db_candidate.role,
        resume_url=db_candidate.resume_url,
        created_at=db_candidate.created_at,
        status=db_candidate.status,
        job_post_id=db_candidate.job_post_id,
        interview_link=db_candidate.interview_link,
        interview_link_expires_at=db_candidate.interview_link_expires_at,
    )


def update_candidate_status(db: Session, candidate_id: str, status: str) -> Candidate | None:
    """Update candidate status."""
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        return None

    candidate.status = status
    db.commit()
    db.refresh(candidate)

    return Candidate(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        role=candidate.role,
        resume_url=candidate.resume_url,
        created_at=candidate.created_at,
        status=candidate.status,
        job_post_id=candidate.job_post_id,
        interview_link=candidate.interview_link,
        interview_link_expires_at=candidate.interview_link_expires_at,
    )
