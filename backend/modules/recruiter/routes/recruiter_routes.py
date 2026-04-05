from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.security.rbac import require_admin, require_recruiter
from backend.infrastructure.database.database import get_db
from backend.models.evaluation_dashboard import (
    EvaluationDashboardResponse,
    ExperimentCompareRequest,
    ExperimentCreateRequest,
)
from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateCreate,
    CandidateInterviewReport,
    JobPost,
    JobPostCreate,
    JobPostUpdate,
    SkillAnalytics,
)
from backend.services.decision_support_service import generate_full_report
from backend.services.evaluation_dashboard_store import (
    compare_experiments,
    get_db_metrics_aggregates,
    get_evaluation_dashboard,
    get_experiments,
    get_historical_trends,
    log_experiment,
)
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

@router.get("/evaluation-dashboard", response_model=EvaluationDashboardResponse)
async def get_ai_evaluation_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_admin)
):
    return await get_evaluation_dashboard(db)


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

# =========================================================
# New API Endpoints for Dashboard Enhancements
# =========================================================

@router.get("/metrics/aggregates")
async def get_metrics_aggregates(
    user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics from PostgreSQL (last 24h, 7d, 30d)."""
    return await get_db_metrics_aggregates(db)


@router.get("/metrics/trends")
async def get_metrics_trends(
    user=Depends(require_admin),
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical trend data for charts."""
    return await get_historical_trends(db, days=days)


@router.get("/experiments")
async def get_experiment_list(
    user=Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get list of experiments."""
    return await get_experiments(db, limit=limit)


@router.post("/experiments")
async def create_experiment(
    payload: ExperimentCreateRequest,
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Log a new experiment result."""
    return await log_experiment(
        db,
        experiment_name=payload.experiment_name,
        model_version=payload.model_version,
        prompt_template=payload.prompt_template,
        accuracy=payload.accuracy,
        latency_ms=payload.latency_ms,
    )


@router.post("/experiments/compare")
async def compare_experiment_results(
    payload: ExperimentCompareRequest,
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Compare multiple experiments."""
    return await compare_experiments(db, payload.experiment_names)


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
