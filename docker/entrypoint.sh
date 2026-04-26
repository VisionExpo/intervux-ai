#!/bin/bash
# =============================================================================
# Intervux AI - Docker Entrypoint
# =============================================================================
# Runs database migrations via Alembic before handing off to the main process.
# This ensures schema is always up to date on container restart/deploy without
# relying on Base.metadata.create_all (which silently ignores column additions).
# =============================================================================

set -e

echo "[entrypoint] Waiting for database to be ready..."

# Poll until PostgreSQL accepts connections (max ~40s)
MAX_TRIES=20
TRIES=0
until python -c "
import os, sys, asyncio
import asyncpg

async def check_db():
    try:
        url = os.environ.get('DATABASE_URL', '')
        if url.startswith('postgresql+asyncpg://'):
            url = url.replace('postgresql+asyncpg://', 'postgresql://')
        conn = await asyncpg.connect(url)
        await conn.close()
        sys.exit(0)
    except Exception as e:
        print(f'  DB not ready: {e}', file=sys.stderr)
        sys.exit(1)

asyncio.run(check_db())
" 2>&1; do
    TRIES=$((TRIES + 1))
    if [ "$TRIES" -ge "$MAX_TRIES" ]; then
        echo "[entrypoint] Database did not become ready in time. Aborting."
        exit 1
    fi
    echo "[entrypoint] Retrying in 2s... ($TRIES/$MAX_TRIES)"
    sleep 2
done

echo "[entrypoint] Database is ready."

RUN_DB_MIGRATIONS="${RUN_DB_MIGRATIONS:-true}"
if [ "$RUN_DB_MIGRATIONS" = "true" ]; then
    echo "[entrypoint] Running database migration manager..."
    python -m backend.infrastructure.database.migration_manager
    
    # Mark migrations as handled so bootstrap.py skips them
    export SKIP_APP_MIGRATIONS=true
else
    echo "[entrypoint] Skipping Alembic migrations (RUN_DB_MIGRATIONS=$RUN_DB_MIGRATIONS)."
fi

# -----------------------------------------------------------------------------
# Log Rotation Permission Fix
# -----------------------------------------------------------------------------
# If logs dir is a bind mount from host, it might be owned by root.
# We need to ensure the container user can rename files inside it (rotation).
if [ -d "/app/logs" ]; then
    echo "[entrypoint] Ensuring /app/logs is writable for rotation..."
    # We can't chown if we are already 'appuser', but we can check if it's writable
    if [ ! -w "/app/logs" ]; then
        echo "[entrypoint] WARNING: /app/logs is NOT writable. Log rotation will fail."
    fi
fi

echo "[entrypoint] Migrations complete. Starting application..."

# Hand off to the CMD from Dockerfile (uvicorn / celery worker / etc.)
exec "$@"
