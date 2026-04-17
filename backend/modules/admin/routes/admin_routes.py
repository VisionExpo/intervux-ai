from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.security.rbac import require_admin, require_recruiter
from backend.infrastructure.database.database import get_db
from backend.models.evaluation_dashboard import (
    EvaluationDashboardResponse,
    ExperimentCompareRequest,
    ExperimentCreateRequest,
)
from backend.services.evaluation_dashboard_store import (
    compare_experiments,
    get_db_metrics_aggregates,
    get_evaluation_dashboard,
    get_experiments,
    get_historical_trends,
    log_experiment,
)

router = APIRouter(tags=["admin-dashboard"], prefix="/admin")

@router.get("/evaluation-dashboard", response_model=EvaluationDashboardResponse)
async def get_ai_evaluation_dashboard(
    db: Session = Depends(get_db),
    user=Depends(require_recruiter)
):
    return await get_evaluation_dashboard(db)


@router.get("/metrics/aggregates")
async def get_metrics_aggregates(
    user=Depends(require_recruiter),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics from PostgreSQL (last 24h, 7d, 30d)."""
    return await get_db_metrics_aggregates(db)


@router.get("/metrics/trends")
async def get_metrics_trends(
    user=Depends(require_recruiter),
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
