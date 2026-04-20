from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security.rbac import require_recruiter
from backend.infrastructure.database.database import get_db
from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateCreate,
    CandidateInterviewReport,
    JobPost,
    JobPostCreate,
    JobPostUpdate,
    SkillAnalytics,
    RecruiterDashboardData,
)
from backend.services.decision_support_service import generate_full_report

from backend.services.recruiter_dashboard_store import (
    compare_candidates,
    create_job_post,
    delete_job_post,
    generate_interview_link,
    get_interview_report,
    get_job_post,
    get_skill_analytics,
    invite_candidate,
    list_candidates,
    list_job_posts,
    update_candidate_status,
    update_job_post,
)

router = APIRouter(tags=["recruiter-dashboard"])

@router.get("/dashboard", response_model=RecruiterDashboardData)
async def get_recruiter_dashboard(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Aggregate recruiter dashboard data."""
    # This is a complex query to get stats
    from backend.models.recruiter_dashboard_models import JobPost as JobPostModel, Candidate as CandidateModel, Interview as InterviewModel, JobPostStatus, CandidateStatus
    from sqlalchemy import func

    # Jobs count
    jobs_count = db.query(func.count(JobPostModel.id)).filter(JobPostModel.status == JobPostStatus.ACTIVE.value).scalar()
    
    # Candidates count
    candidates_count = db.query(func.count(CandidateModel.id)).scalar()

    # Pipeline stats
    pipeline_stats = []
    for status in [CandidateStatus.INVITED, CandidateStatus.IN_PROGRESS, CandidateStatus.COMPLETED]:
        count = db.query(func.count(CandidateModel.id)).filter(CandidateModel.status == status.value).scalar()
        pipeline_stats.append({"stage": status.value.capitalize(), "count": str(count)})

    # Recent candidates
    candidates_list = await list_candidates(db, limit=5)
    
    # Activity stream (mock for now as there is no activity table, but pulling from latest completions)
    recent_interviews = db.query(InterviewModel).order_by(InterviewModel.completed_at.desc()).limit(5).all()
    activity = []
    for interview in recent_interviews:
        if interview.completed_at:
            activity.append(f"Interview for {interview.role} completed with score {interview.overall_score or 0:.0f}")

    return {
        "candidates": candidates_list,
        "stats": {
            "openRoles": str(jobs_count),
            "activeCandidates": str(candidates_count),
            "avgTime": "2.4d", # Mocked for now, need historical tracking
            "alignmentScore": "94%", # Mocked
        },
        "pipeline": pipeline_stats,
        "activity_stream": activity if activity else ["No recent activity"],
    }



@router.get("/candidates")
async def get_candidates(
    user=Depends(require_recruiter),
    page: int = 1,
    limit: int = 20,
    role: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return await list_candidates(db, page=page, limit=limit, role=role, search=search)


@router.get("/interview/{interview_id}", response_model=CandidateInterviewReport)
async def get_interview(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return await get_interview_report(db, interview_id)


@router.get("/interview/{interview_id}/analytics", response_model=SkillAnalytics)
async def get_interview_analytics(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return await get_skill_analytics(db, interview_id)


@router.get("/candidates/compare", response_model=list[CandidateComparisonRow])
async def get_candidate_comparison(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return await compare_candidates(db)



@router.post("/interview/{interview_id}/decision")
async def get_interview_decision(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Get decision support for an interview."""
    interview = await get_interview_report(db, interview_id)

    if hasattr(interview, "model_dump"):
        interview_data = interview.model_dump()
    elif isinstance(interview, dict):
        interview_data = interview
    else:
        interview_data = {}

    answers = interview_data.get("answers")
    if not isinstance(answers, list):
        questions = interview_data.get("questions", [])
        answers = []
        if isinstance(questions, list):
            for question_item in questions:
                if not isinstance(question_item, dict):
                    continue
                score = float(question_item.get("score", 0) or 0)
                answers.append(
                    {
                        "question": question_item.get("question", ""),
                        "answer": question_item.get("answer", ""),
                        "score": score,
                        "evaluation": {
                            "scores": {
                                "Overall": score,
                                "Technical": score,
                                "Behavioral": score,
                                "Reasoning": score,
                            }
                        },
                    }
                )

    profile = interview_data.get("profile") or interview_data.get("candidate")

    report = generate_full_report(
        answers=answers,
        profile=profile,
    )
    return report

# =========================================================
# Job Post API Endpoints
# =========================================================

@router.get("/job-posts", response_model=list[JobPost])
async def get_job_posts(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
):
    """Get list of job posts."""
    return await list_job_posts(db, page=page, limit=limit, status=status)


@router.post("/job-posts", response_model=JobPost)
async def create_new_job_post(
    job_data: JobPostCreate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Create a new job post."""
    return await create_job_post(db, job_data, created_by=user.user_id)


@router.get("/job-posts/{job_post_id}", response_model=JobPost)
async def get_job(
    job_post_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Get a single job post."""
    job = await get_job_post(db, job_post_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job post not found")
    return job


@router.put("/job-posts/{job_post_id}", response_model=JobPost)
async def update_job(
    job_post_id: str,
    job_data: JobPostUpdate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Update a job post."""
    job = await update_job_post(db, job_post_id, job_data)
    if not job:
        raise HTTPException(status_code=404, detail="Job post not found")
    return job


@router.delete("/job-posts/{job_post_id}")
async def delete_job(
    job_post_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Delete a job post."""
    success = await delete_job_post(db, job_post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job post not found")
    return {"message": "Job post deleted successfully"}

# =========================================================
# Candidate API Endpoints
# =========================================================

@router.post("/candidates/invite", response_model=dict)
async def invite_new_candidate(
    candidate_data: CandidateCreate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Invite a candidate to a job."""
    candidate = await invite_candidate(db, candidate_data)
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "role": candidate.role,
        "status": candidate.status,
    }


@router.post("/candidates/{candidate_id}/generate-link")
async def create_interview_link(
    candidate_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
    expires_days: int = 7,
):
    """Generate an interview link for a candidate."""
    interview_link, expires_at = await generate_interview_link(db, candidate_id, expires_days)
    return {
        "interview_link": interview_link,
        "expires_at": expires_at.isoformat(),
    }


@router.patch("/candidates/{candidate_id}/status")
async def change_candidate_status(
    candidate_id: str,
    status: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Update candidate status."""
    candidate = await update_candidate_status(db, candidate_id, status)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
