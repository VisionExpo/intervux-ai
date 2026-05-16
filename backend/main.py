import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure absolute imports like `from backend...` work
if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from backend.infrastructure.bootstrap import bootstrap_system
from backend.core.config.settings import get_settings
from backend.core.logging.logger import get_logger
from backend.api.middleware.security import SecurityHeadersMiddleware
from backend.api.middleware.observability import ObservabilityMiddleware
from backend.api.middleware.error_handler import register_error_handlers
from backend.api.middleware.rate_limiter import RateLimitMiddleware

# Modules / Routers
from backend.api.routes.auth_routes import router as auth_router
from backend.modules.candidate.routes.candidate_routes import router as candidate_router
from backend.modules.candidate.routes.resume_routes import router as resume_router
from backend.modules.recruiter.routes.recruiter_routes import router as recruiter_router
from backend.modules.admin.routes.admin_routes import router as admin_router
from backend.modules.admin.routes.admin_compat_routes import router as admin_compat_router
from backend.modules.analytics.routes.metrics_routes import router as metrics_router
from backend.api.routes.system import router as system_router

# Real-time / Sockets
from backend.modules.interview.websocket.interview_gateway import InterviewGateway
from backend.modules.analytics.websocket.metrics_socket import metrics_socket
from backend.utils.runtime_monitor import RuntimeMonitor

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    # 1. ThreadPool Setup
    workers = settings.runtime_threadpool_workers
    thread_pool = ThreadPoolExecutor(max_workers=workers)
    import asyncio
    loop = asyncio.get_running_loop()
    loop.set_default_executor(thread_pool)
    app.state.thread_pool = thread_pool

    # 2. Bootstrap (Migrations, Pre-warming)
    await bootstrap_system()

    # 3. Start Monitor
    if hasattr(app.state, "runtime_monitor"):
        await app.state.runtime_monitor.start()

    # 4. Start Metrics Broadcast
    from backend.modules.analytics.websocket.metrics_socket import start_metrics_broadcast
    metrics_task = asyncio.create_task(start_metrics_broadcast())
    app.state.metrics_broadcast_task = metrics_task

    yield

    # 5. Shutdown
    # Stop Metrics Broadcast
    from backend.modules.analytics.websocket.metrics_socket import stop_metrics_broadcast
    await stop_metrics_broadcast()
    
    if hasattr(app.state, "metrics_broadcast_task"):
        task = app.state.metrics_broadcast_task
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, concurrent.futures.CancelledError, getattr(concurrent.futures, "_base", concurrent.futures).CancelledError):
            pass
        logger.info("Metrics broadcast task shutdown cleanly")
    if hasattr(app.state, "interview_gateway"):
        await app.state.interview_gateway.shutdown()
    if hasattr(app.state, "runtime_monitor"):
        await app.state.runtime_monitor.stop()
    
    thread_pool.shutdown(wait=False, cancel_futures=True)


def create_app() -> FastAPI:
    """
    App Factory Pattern.
    """
    app = FastAPI(
        title="Intervux-AI",
        description="Production-grade AI Interview SaaS",
        version="1.0.0",
        lifespan=lifespan
    )

    # --- Dependency Injection / State ---
    interview_gateway = InterviewGateway(
        total_questions=int(os.getenv("INTERVIEW_TOTAL_QUESTIONS", "10"))
    )
    runtime_monitor = RuntimeMonitor(interview_socket=interview_gateway)
    app.state.interview_gateway = interview_gateway
    app.state.runtime_monitor = runtime_monitor

    # --- Middleware ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ObservabilityMiddleware)

    # --- Error Handlers ---
    register_error_handlers(app)

    # --- WebSockets ---
    @app.websocket("/ws/interview")
    async def websocket_interview(websocket: WebSocket):
        print(f"DEBUG: WebSocket connection received for /ws/interview", flush=True)
        token = websocket.query_params.get("token")
        await app.state.interview_gateway.handle(websocket, token)

    @app.websocket("/ws/metrics")
    async def websocket_metrics(websocket: WebSocket):
        await metrics_socket.handle(websocket)

    # --- Routers ---
    @app.get("/ping")
    def ping():
        return {"ping": "pong"}

    app.include_router(system_router, prefix="/api/system") # Grouped system routes
    
    # Phase 0: Legacy Compatibility Layer (Redirects/Aliases)
    @app.get("/health", include_in_schema=False)
    def legacy_health():
        from backend.api.routes.system import health
        return health()
        
    @app.get("/ready", include_in_schema=False)
    async def legacy_ready():
        from backend.api.routes.system import readiness_check
        return await readiness_check()
        
    @app.get("/metrics", include_in_schema=False)
    def legacy_metrics():
        from backend.api.routes.system import get_metrics
        return get_metrics()

    @app.get("/health/migrations", include_in_schema=False)
    async def legacy_migration_health():
        from backend.api.routes.system import migration_health
        return await migration_health()

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(candidate_router, prefix="/api/candidate", tags=["candidate"])
    app.include_router(resume_router, prefix="/api/resume", tags=["resume"])
    app.include_router(recruiter_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    app.include_router(admin_compat_router, prefix="/api")
    app.include_router(metrics_router, prefix="/api")

    # --- Static Files ---
    uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

    return app


app = create_app()
