import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy import text
from backend.infrastructure.database.database import engine, Base
from backend.core.llm_brain import prewarm_llm
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


async def run_migrations() -> None:
    """
    Run 'alembic upgrade head' as a subprocess or fallback to create_all.
    """
    db_url = os.getenv("DATABASE_URL", "")
    if _is_sqlite(db_url):
        logger.info("SQLite detected — using create_all for dev/test environment")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    # Check for alembic folder in various common locations
    project_root = Path(__file__).resolve().parents[2]
    alembic_path = project_root / "backend" / "db" / "alembic"
    
    if not alembic_path.exists():
        logger.info(f"No alembic folder found at {alembic_path}. Falling back to create_all.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    logger.info("Running Alembic migrations...")
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "alembic", "upgrade", "head",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root)
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"Alembic migration failed:\n{stderr.decode()}")
            # We don't necessarily want to crash the whole app if migrations fail
            # but in production, we might.
        else:
            logger.info("Alembic migrations complete.")
    except Exception as e:
        logger.warning(f"Failed to run alembic: {e}. Falling back to create_all.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


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
