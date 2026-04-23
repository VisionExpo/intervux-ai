import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking request metrics, latency, and session tracing.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Propagate or generate Session ID
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

            # Structured log for request completion
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
