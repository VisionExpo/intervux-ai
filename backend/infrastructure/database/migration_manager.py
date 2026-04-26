import asyncio
import os
import sys
import subprocess
from pathlib import Path
from sqlalchemy import inspect, text
from backend.infrastructure.database.database import engine
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)

REQUIRED_TABLES = ["users", "candidates", "job_posts", "candidate_profiles", "mock_interviews"]
SCHEMA_SIGNATURE = {
    "users": ["id", "email", "password_hash", "name", "role", "is_active", "created_at"],
    "candidates": ["id", "name", "email", "role", "status", "job_post_id"],
    "job_posts": ["id", "title", "experience_level", "status", "ai_interview_enabled"],
    "candidate_profiles": ["id", "user_id", "name", "skills", "experience_years"],
    "mock_interviews": ["id", "candidate_id", "session_id", "status"]
}

async def get_current_revision():
    """Returns the current alembic revision or None."""
    try:
        project_root = Path(__file__).resolve().parents[3]
        result = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "alembic", "current",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(project_root)
        )
        stdout, stderr = await result.communicate()
        output = stdout.decode().strip()
        # Typical output: "003 (head)"
        if output:
            parts = output.split()
            if parts and parts[0] != "Current": # Handle "Current revision(s) for ..." header
                 return parts[0]
            # Sometimes alembic current output is multiline or has headers
            lines = output.splitlines()
            for line in lines:
                if line.strip() and not line.startswith("Context") and not line.startswith("Current"):
                    return line.split()[0]
    except Exception as e:
        logger.error(f"Failed to get current alembic revision: {e}")
    return None

async def check_db_state():
    """
    Analyzes the database to see if it's unversioned but populated.
    Returns (has_alembic, is_populated, schema_validated)
    """
    async with engine.begin() as conn:
        def inspect_sync(sync_conn):
            inspector = inspect(sync_conn)
            has_alembic = inspector.has_table("alembic_version")
            
            existing_tables = inspector.get_table_names()
            
            # 1. Check for required tables
            all_tables_exist = all(t in existing_tables for t in REQUIRED_TABLES)
            is_populated = any(t in existing_tables for t in REQUIRED_TABLES)
            
            if not all_tables_exist:
                return has_alembic, is_populated, False
            
            # 2. Check for required columns (signature check)
            schema_validated = True
            for table, columns in SCHEMA_SIGNATURE.items():
                existing_cols = [c["name"] for c in inspector.get_columns(table)]
                missing = [col for col in columns if col not in existing_cols]
                if missing:
                    logger.warning(f"Table '{table}' signature mismatch. Missing columns: {missing}")
                    schema_validated = False
            
            return has_alembic, True, schema_validated

        return await conn.run_sync(inspect_sync)

async def run_migrations():
    """
    Centralized migration logic used by both entrypoint and application.
    """
    run_db_migrations = os.getenv("RUN_DB_MIGRATIONS", "true").lower() == "true"
    if not run_db_migrations:
        logger.info("RUN_DB_MIGRATIONS is disabled. Skipping.")
        return

    # Check for alembic folder
    project_root = Path(__file__).resolve().parents[3]
    alembic_path = project_root / "backend" / "db" / "alembic"
    if not alembic_path.exists():
        logger.warning(f"No alembic folder found at {alembic_path}. Skipping.")
        return

    has_alembic, is_populated, schema_validated = await check_db_state()
    auto_stamp = os.getenv("AUTO_STAMP_DB", "false").lower() == "true"

    if not has_alembic and is_populated:
        if auto_stamp:
            logger.warning("Detected pre-existing schema without alembic_version. Stamping to head.")
            logger.warning("⚠️  Stamping unverified schema — potential mismatch with migrations")
            try:
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "alembic", "stamp", "head",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(project_root)
                )
                _, stderr = await process.communicate()
                if process.returncode != 0:
                    logger.error(f"Failed to stamp database:\n{stderr.decode()}")
                    sys.exit(1)
            except Exception as e:
                logger.error(f"Failed to stamp database: {e}")
                sys.exit(1)
        else:
            logger.error("CRITICAL: Detected pre-existing schema without alembic_version.")
            logger.error("AUTO_STAMP_DB is disabled. Manual intervention required to verify schema and run 'alembic stamp head'.")
            sys.exit(1)

    logger.info("Running Alembic upgrade head...")
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
            sys.exit(1)
        else:
            logger.info("Alembic migrations complete.")
    except Exception as e:
        logger.error(f"Failed to run alembic: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure explicit exit codes for CI/CD automation
    try:
        asyncio.run(run_migrations())
        sys.exit(0)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.exception(f"Unexpected error in migration manager: {e}")
        sys.exit(1)
