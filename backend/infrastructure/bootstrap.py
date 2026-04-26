import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy import inspect, text
from backend.infrastructure.database.database import engine, Base
from backend.core.llm_brain import prewarm_llm
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


async def run_migrations() -> None:
    """
    Coordinates Alembic migrations via the centralized migration manager.
    """
    from backend.infrastructure.database.migration_manager import run_migrations as central_run_migrations
    
    # 1. Skip if already handled by entrypoint (Docker)
    skip_migrations = os.getenv("SKIP_APP_MIGRATIONS") == "true"
    if skip_migrations:
        from backend.infrastructure.database.migration_manager import check_db_state
        has_alembic, _, _ = await check_db_state()
        if not has_alembic:
            logger.critical("Invalid state: SKIP_APP_MIGRATIONS is true but database is not initialized.")
            raise RuntimeError("Database not initialized. Migration manager must run before application startup.")
        logger.info("SKIP_APP_MIGRATIONS is set. Skipping application-level migration check.")
        return

    await central_run_migrations()


async def bootstrap_system() -> None:
    """
    Coordinates non-blocking bootstrap tasks.
    """
    # 1. Ensure DB is ready
    db_ready = False
    for _ in range(20):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            db_ready = True
            break
        except Exception:
            await asyncio.sleep(1.5)

    if not db_ready:
        logger.error("Database was not ready during startup window. Migrations may fail.")

    # 2. Run migrations
    await run_migrations()

    # 3. Non-blocking LLM pre-warming
    asyncio.create_task(asyncio.to_thread(prewarm_llm))
    logger.info("Bootstrap sequence complete. LLM pre-warming in background.")
