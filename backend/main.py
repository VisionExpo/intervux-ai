import time
import uuid
import asyncio
import os
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from backend.models.evaluation_dashboard import (
    EvaluationDashboardResponse,
    ExperimentCompareRequest,
    ExperimentCreateRequest,
)
from backend.db.database import Base, engine, get_db
from backend.core.llm_brain import prewarm_llm
from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateCreate,
    CandidateInterviewReport,
    JobPost,
    JobPostCreate,
    JobPostUpdate,
    SkillAnalytics,
)
from backend.services.recruiter_dashboard_store import (
    compare_candidates,
    create_job_post,
    get_interview_report,
    get_job_post,
    get_skill_analytics,
    list_candidates,
    list_job_posts,
    update_job_post,
    delete_job_post,
    generate_interview_link,
    invite_candidate,
    update_candidate_status,
)
from backend.services.evaluation_dashboard_store import (
    get_evaluation_dashboard,
    get_db_metrics_aggregates,
    get_historical_trends,
    get_experiments,
    log_experiment,
    compare_experiments,
)
from backend.services.decision_support_service import generate_full_report
from backend.models import recruiter_dashboard_models  # noqa: F401
from backend.sockets.interview import InterviewSocket
from backend.sockets.metrics import metrics_socket
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics
from backend.utils.runtime_monitor import RuntimeMonitor

# Auth imports
from backend.auth import get_current_user
from backend.auth.routes import router as auth_router
from backend.auth.rbac import require_recruiter, require_admin
from backend.middleware.rate_limiter import RateLimitMiddleware
from backend.routes.candidate_routes import router as candidate_router

logger = get_logger(__name__)
interview_socket = InterviewSocket(total_questions=2)
runtime_monitor = RuntimeMonitor(interview_socket=interview_socket)
thread_pool: ThreadPoolExecutor | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global thread_pool
    workers = int(os.getenv("RUNTIME_THREADPOOL_WORKERS", "4"))
    Base.metadata.create_all(bind=engine)
    loop = asyncio.get_running_loop()
    thread_pool = ThreadPoolExecutor(max_workers=workers)
    loop.set_default_executor(thread_pool)
    await runtime_monitor.start()
    await asyncio.to_thread(prewarm_llm)
    try:
        yield
    finally:
        await interview_socket.shutdown()
        await runtime_monitor.stop()
        if thread_pool is not None:
            thread_pool.shutdown(wait=False, cancel_futures=True)
            thread_pool = None


app = FastAPI(title="Intervux-AI", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add security headers middleware
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        return response


app.add_middleware(SecurityHeadersMiddleware)

# Include auth router
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])

# Include candidate portal router
app.include_router(candidate_router, prefix="/api/candidate", tags=["candidate"])


@app.middleware("http")
async def add_observability(request: Request, call_next):
    session_id = request.headers.get("X-Session-ID", str(uuid.uuid4()))
    start = time.time()

    metrics.record_request()

    try:
        response = await call_next(request)
        return response
    except Exception:
        metrics.record_error()
        logger.exception(
            "Unhandled exception",
            extra={"extra_data": {"session_id": session_id}},
        )
        raise
    finally:
        duration = round(time.time() - start, 3)
        metrics.record_latency("request_total", duration)

        logger.info(
            "Request processed",
            extra={
                "extra_data": {
                    "session_id": session_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration": duration,
                }
            },
        )


@app.get("/health")
def health():
    """Basic health check endpoint."""
    return {"status": "ok"}


@app.get("/ready")
def readiness_check():
    """
    Readiness check endpoint for Kubernetes/load balancers.
    
    Checks:
    - Database connectivity
    - LLM service availability
    """
    checks = {
        "status": "ok",
        "database": "unknown",
    }
    
    # Check database connectivity
    try:
        from sqlalchemy import text
        from backend.db.database import SessionLocal
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = "disconnected"
        checks["status"] = "degraded"
    
    # Overall status
    if checks["database"] != "connected":
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail=checks)
    
    return checks


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@app.get("/api/evaluation-dashboard", response_model=EvaluationDashboardResponse)
def get_ai_evaluation_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_recruiter)
):
    return get_evaluation_dashboard(db)


@app.get("/api/candidates")
def get_candidates(
    user=Depends(require_recruiter),
    page: int = 1,
    limit: int = 20,
    role: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return list_candidates(db, page=page, limit=limit, role=role, search=search)


@app.get("/api/interview/{interview_id}", response_model=CandidateInterviewReport)
def get_interview(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return get_interview_report(db, interview_id)


@app.get("/api/interview/{interview_id}/analytics", response_model=SkillAnalytics)
def get_interview_analytics(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return get_skill_analytics(db, interview_id)


@app.get("/api/candidates/compare", response_model=list[CandidateComparisonRow])
def get_candidate_comparison(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    return compare_candidates(db)


@app.websocket("/ws/interview")
async def websocket_interview(ws: WebSocket):
    await interview_socket.handle(ws)


@app.websocket("/ws/metrics")
async def websocket_metrics(ws: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    await metrics_socket.handle(ws)


# =========================================================
# New API Endpoints for Dashboard Enhancements
# =========================================================

@app.get("/api/metrics/aggregates")
def get_metrics_aggregates(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics from PostgreSQL (last 24h, 7d, 30d)."""
    return get_db_metrics_aggregates(db)


@app.get("/api/metrics/trends")
def get_metrics_trends(
    user=Depends(require_recruiter),
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical trend data for charts."""
    return get_historical_trends(db, days=days)


@app.get("/api/experiments")
def get_experiment_list(
    user=Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get list of experiments."""
    return get_experiments(db, limit=limit)


@app.post("/api/experiments")
def create_experiment(
    payload: ExperimentCreateRequest,
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Log a new experiment result."""
    return log_experiment(
        db,
        experiment_name=payload.experiment_name,
        model_version=payload.model_version,
        prompt_template=payload.prompt_template,
        accuracy=payload.accuracy,
        latency_ms=payload.latency_ms,
    )


@app.post("/api/experiments/compare")
def compare_experiment_results(
    payload: ExperimentCompareRequest,
    user=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Compare multiple experiments."""
    return compare_experiments(db, payload.experiment_names)


@app.post("/api/interview/{interview_id}/decision")
def get_interview_decision(
    interview_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Get decision support for an interview."""
    # Get interview report
    interview = get_interview_report(db, interview_id)

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

    # Generate decision support report
    report = generate_full_report(
        answers=answers,
        profile=profile,
    )
    
    return report


# =========================================================
# Job Post API Endpoints
# =========================================================


@app.get("/api/job-posts", response_model=list[JobPost])
def get_job_posts(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 20,
    status: str | None = None,
):
    """Get list of job posts."""
    return list_job_posts(db, page=page, limit=limit, status=status)


@app.post("/api/job-posts", response_model=JobPost)
def create_new_job_post(
    job_data: JobPostCreate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Create a new job post."""
    return create_job_post(db, job_data, created_by=user.user_id)


@app.get("/api/job-posts/{job_post_id}", response_model=JobPost)
def get_job(
    job_post_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Get a single job post."""
    job = get_job_post(db, job_post_id)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job post not found")
    return job


@app.put("/api/job-posts/{job_post_id}", response_model=JobPost)
def update_job(
    job_post_id: str,
    job_data: JobPostUpdate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Update a job post."""
    job = update_job_post(db, job_post_id, job_data)
    if not job:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job post not found")
    return job


@app.delete("/api/job-posts/{job_post_id}")
def delete_job(
    job_post_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Delete a job post."""
    success = delete_job_post(db, job_post_id)
    if not success:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job post not found")
    return {"message": "Job post deleted successfully"}


# =========================================================
# Candidate API Endpoints
# =========================================================


@app.post("/api/candidates/invite", response_model=dict)
def invite_new_candidate(
    candidate_data: CandidateCreate,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Invite a candidate to a job."""
    candidate = invite_candidate(db, candidate_data)
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "role": candidate.role,
        "status": candidate.status,
    }


@app.post("/api/candidates/{candidate_id}/generate-link")
def create_interview_link(
    candidate_id: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
    expires_days: int = 7,
):
    """Generate an interview link for a candidate."""
    interview_link, expires_at = generate_interview_link(db, candidate_id, expires_days)
    return {
        "interview_link": interview_link,
        "expires_at": expires_at.isoformat(),
    }


@app.patch("/api/candidates/{candidate_id}/status")
def change_candidate_status(
    candidate_id: str,
    status: str,
    user=Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Update candidate status."""
    candidate = update_candidate_status(db, candidate_id, status)
    if not candidate:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# =========================================================
# Static Files (Uploads)
# =========================================================

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Mount static files for uploaded resumes
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

