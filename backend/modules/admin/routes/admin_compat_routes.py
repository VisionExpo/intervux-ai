from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.security.rbac import require_admin
from backend.infrastructure.database.database import get_db
from backend.services.evaluation_dashboard_store import get_experiments

# Backward-compatible admin route aliases kept for older clients/tests.
router = APIRouter(tags=["admin-dashboard-compat"])


@router.get("/experiments")
async def get_experiment_list_compat(
    user=Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 100,
):
    return await get_experiments(db, limit=limit)

