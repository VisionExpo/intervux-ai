from fastapi import APIRouter, Depends

from backend.core.security.rbac import require_recruiter

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/aggregates")
async def get_metrics_aggregates(user=Depends(require_recruiter)):
    """Get high-level metrics aggregates."""
    return {
        "last_24h": {"interviews": 12, "avg_score": 85.5},
        "last_7d": {"interviews": 45, "avg_score": 82.1},
        "last_30d": {"interviews": 120, "avg_score": 84.0}
    }


@router.get("/trends")
async def get_metrics_trends(days: int = 30, user=Depends(require_recruiter)):
    """Get metric trends for the specified number of days."""
    return {
        "dates": ["2026-04-01", "2026-04-02", "2026-04-03"],
        "latency": [120, 115, 130],
        "accuracy": [0.85, 0.86, 0.88]
    }
