import time
import uuid
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

from fastapi import Depends, FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.models.evaluation_dashboard import EvaluationDashboardResponse
from backend.db.database import Base, engine, get_db
from backend.core.llm_brain import prewarm_llm
from backend.models.recruiter_dashboard import (
    CandidateComparisonRow,
    CandidateInterviewReport,
    SkillAnalytics,
)
from backend.services.recruiter_dashboard_store import (
    compare_candidates,
    get_interview_report,
    get_skill_analytics,
    list_candidates,
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

logger = get_logger(__name__)
interview_socket = InterviewSocket(total_questions=2)
runtime_monitor = RuntimeMonitor(interview_socket=interview_socket)
thread_pool: ThreadPoolExecutor | None = None

app = FastAPI(title="Intervux-AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@app.get("/api/evaluation-dashboard", response_model=EvaluationDashboardResponse)
def get_ai_evaluation_dashboard(db: Session = Depends(get_db)):
    return get_evaluation_dashboard(db)


@app.get("/api/candidates")
def get_candidates(
    page: int = 1,
    limit: int = 20,
    role: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    return list_candidates(db, page=page, limit=limit, role=role, search=search)


@app.get("/api/interview/{interview_id}", response_model=CandidateInterviewReport)
def get_interview(interview_id: str, db: Session = Depends(get_db)):
    return get_interview_report(db, interview_id)


@app.get("/api/interview/{interview_id}/analytics", response_model=SkillAnalytics)
def get_interview_analytics(interview_id: str, db: Session = Depends(get_db)):
    return get_skill_analytics(db, interview_id)


@app.get("/api/candidates/compare", response_model=list[CandidateComparisonRow])
def get_candidate_comparison(db: Session = Depends(get_db)):
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
def get_metrics_aggregates(db: Session = Depends(get_db)):
    """Get aggregated metrics from PostgreSQL (last 24h, 7d, 30d)."""
    return get_db_metrics_aggregates(db)


@app.get("/api/metrics/trends")
def get_metrics_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get historical trend data for charts."""
    return get_historical_trends(db, days=days)


@app.get("/api/experiments")
def get_experiment_list(db: Session = Depends(get_db), limit: int = 100):
    """Get list of experiments."""
    return get_experiments(db, limit=limit)


@app.post("/api/experiments")
def create_experiment(
    experiment_name: str,
    model_version: str,
    prompt_template: str,
    accuracy: float = None,
    latency_ms: int = None,
    db: Session = Depends(get_db),
):
    """Log a new experiment result."""
    return log_experiment(
        db,
        experiment_name=experiment_name,
        model_version=model_version,
        prompt_template=prompt_template,
        accuracy=accuracy,
        latency_ms=latency_ms,
    )


@app.post("/api/experiments/compare")
def compare_experiment_results(
    experiment_names: list[str],
    db: Session = Depends(get_db),
):
    """Compare multiple experiments."""
    return compare_experiments(db, experiment_names)


@app.post("/api/interview/{interview_id}/decision")
def get_interview_decision(
    interview_id: str,
    db: Session = Depends(get_db),
):
    """Get decision support for an interview."""
    # Get interview report
    interview = get_interview_report(db, interview_id)
    
    if not interview:
        return {"error": "Interview not found"}
    
    # Generate decision support report
    report = generate_full_report(
        answers=interview.get("answers", []),
        profile=interview.get("profile"),
    )
    
    return report


@app.on_event("startup")
async def on_startup():
    global thread_pool
    workers = int(os.getenv("RUNTIME_THREADPOOL_WORKERS", "4"))
    Base.metadata.create_all(bind=engine)
    loop = asyncio.get_running_loop()
    thread_pool = ThreadPoolExecutor(max_workers=workers)
    loop.set_default_executor(thread_pool)
    await runtime_monitor.start()
    await asyncio.to_thread(prewarm_llm)


@app.on_event("shutdown")
async def on_shutdown():
    await interview_socket.shutdown()
    await runtime_monitor.stop()
    global thread_pool
    if thread_pool is not None:
        thread_pool.shutdown(wait=False, cancel_futures=True)
        thread_pool = None
