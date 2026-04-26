from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from backend.infrastructure.database.database import AsyncSessionLocal
from backend.utils.metrics import metrics
from backend.services.redis_manager import redis_client

router = APIRouter(tags=["system"])


@router.get("/health")
def health():
    """Basic Liveness check."""
    return {"status": "ok"}


@router.get("/ready")
async def readiness_check():
    """
    Enhanced Readiness check for production environments.
    Checks connectivity to:
    - PostgreSQL
    - Redis
    """
    checks = {
        "status": "ok",
        "database": "unknown",
        "redis": "unknown",
    }
    
    # 1. Check database connectivity
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception:
        checks["database"] = "disconnected"
        checks["status"] = "degraded"
    
    # 2. Check Redis connectivity
    try:
        if await redis_client.redis.ping():
            checks["redis"] = "connected"
        else:
            checks["redis"] = "disconnected"
            checks["status"] = "degraded"
    except Exception:
        checks["redis"] = "disconnected"
        checks["status"] = "degraded"
    
    # Overall status
    if checks["status"] != "ok":
        raise HTTPException(status_code=503, detail=checks)
    
    return checks


@router.get("/metrics")
def get_metrics():
    """Returns a snapshot of system metrics."""
    return metrics.snapshot()


@router.get("/health/migrations")
async def migration_health():
    """Returns the current state of database migrations."""
    import os
    from backend.infrastructure.database.migration_manager import get_current_revision, check_db_state
    
    revision = await get_current_revision()
    has_alembic, is_populated, schema_validated = await check_db_state()
    auto_stamp = os.getenv("AUTO_STAMP_DB", "false").lower() == "true"
    
    severity = "ok"
    if not has_alembic and is_populated:
        severity = "critical"
    elif not schema_validated:
        severity = "warning"
    elif not has_alembic:
        severity = "info"

    return {
        "revision": revision,
        "alembic_initialized": has_alembic,
        "is_populated": is_populated,
        "schema_validated": schema_validated,
        "status": "up-to-date" if revision else "unversioned",
        "mode": "auto-heal" if auto_stamp else "strict",
        "severity": severity,
        "safe": has_alembic and schema_validated
    }
