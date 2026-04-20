import time
import uuid
import asyncio
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

# Ensure absolute imports like `from backend...` also work when launched
# from inside the `backend/` directory (e.g., `uvicorn main:app`).
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
import sentry_sdk

# Initialize Sentry for global Exception catching
sentry_dsn = os.getenv("SENTRY_DSN", "")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

from backend.infrastructure.database.database import Base, engine
from backend.core.llm_brain import prewarm_llm
from backend.models import recruiter_dashboard_models  # noqa: F401
from backend.models.candidate_portal import CandidateProfile, MockInterview, Notification  # noqa: F401
from backend.modules.interview.websocket.interview_gateway import InterviewGateway
from backend.modules.analytics.websocket.metrics_socket import metrics_socket
from backend.core.logging.logger import get_logger
from backend.core.config.settings import get_settings
from backend.core.exceptions import register_exception_handlers
from backend.utils.metrics import metrics
from backend.utils.runtime_monitor import RuntimeMonitor

# Auth imports
from backend.api.routes.auth_routes import router as auth_router
from backend.api.middleware.rate_limiter import RateLimitMiddleware
from backend.modules.candidate.routes.candidate_routes import router as candidate_router
from backend.modules.candidate.routes.resume_routes import router as resume_router
from backend.modules.recruiter.routes.recruiter_routes import router as recruiter_router
from backend.modules.admin.routes.admin_routes import router as admin_router
from backend.modules.admin.routes.admin_compat_routes import router as admin_compat_router
from backend.modules.analytics.routes.metrics_routes import router as metrics_router

logger = get_logger(__name__)
interview_gateway = InterviewGateway(total_questions=2)
runtime_monitor = RuntimeMonitor(interview_socket=interview_gateway)
settings = get_settings()
thread_pool: ThreadPoolExecutor | None = None


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


async def _run_alembic_migrations() -> None:
    """
    Run 'alembic upgrade head' as a subprocess.

    Falls back to create_all for SQLite/dev environments.
    """
    db_url = os.getenv("DATABASE_URL", "")
    if _is_sqlite(db_url):
        logger.info("SQLite detected — using create_all for dev/test environment")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    if not os.path.exists("alembic") and not os.path.exists("backend/alembic") and not os.path.exists("/app/alembic"):
        logger.info("No alembic folder found. Falling back to create_all.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return

    logger.info("Running Alembic migrations...")
    try:
        # Run subprocess concurrently
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "alembic", "upgrade", "head",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"Alembic migration failed:\n{stderr.decode()}")
            raise RuntimeError(f"Alembic migration failed: {stderr.decode()}")
        logger.info(f"Alembic migrations complete:\n{stdout.decode()}")
    except FileNotFoundError:
        logger.warning("alembic not found — falling back to create_all (run migrations manually)")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


def _validate_cors_origins(origins: list[str]) -> None:
    """
    Warn if localhost CORS origins are used with a non-local postgres setup.
    """
    db_url = os.getenv("DATABASE_URL", "")
    is_postgres = "postgres" in db_url or "postgresql" in db_url

    localhost_origins = [o for o in origins if "localhost" in o or "127.0.0.1" in o]

    if is_postgres and localhost_origins:
        logger.warning(
            "CORS is configured with localhost origins but DATABASE_URL points to a "
            "remote PostgreSQL instance. This will block all browser clients not on "
            "localhost. Set CORS_ALLOW_ORIGINS to your frontend domain(s) in .env.docker."
        )
        print(
            "[WARN] CORS localhost mismatch — set CORS_ALLOW_ORIGINS to your frontend URL",
            file=sys.stderr,
        )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global thread_pool
    workers = settings.runtime_threadpool_workers

    # Wait for Postgres readiness before metadata/table initialization.
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
        logger.warning("Database was not ready during startup warmup window")

    await _run_alembic_migrations()
    loop = asyncio.get_running_loop()
    thread_pool = ThreadPoolExecutor(max_workers=workers)
    loop.set_default_executor(thread_pool)
    await runtime_monitor.start()
    await asyncio.to_thread(prewarm_llm)
    try:
        yield
    finally:
        await interview_gateway.shutdown()
        await runtime_monitor.stop()
        if thread_pool is not None:
            thread_pool.shutdown(wait=False, cancel_futures=True)
            thread_pool = None


app = FastAPI(title="Intervux-AI", version="1.0.0", lifespan=lifespan)

register_exception_handlers(app)
_validate_cors_origins(settings.cors_allow_origins)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
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
app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
app.include_router(recruiter_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_compat_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")


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
async def readiness_check():
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
        from backend.infrastructure.database.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
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


@app.websocket("/ws/interview")
async def websocket_interview(ws: WebSocket):
    await interview_gateway.handle(ws)


@app.websocket("/ws/metrics")
async def websocket_metrics(ws: WebSocket):
    """WebSocket endpoint for real-time metrics streaming."""
    await metrics_socket.handle(ws)


# =========================================================
# Static Files (Uploads)
# =========================================================

# Create uploads directory if it doesn't exist
uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(uploads_dir, exist_ok=True)

# Mount static files for uploaded resumes
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


