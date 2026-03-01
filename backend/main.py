import time
import uuid

from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from backend.sockets.interview import InterviewSocket
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)
interview_socket = InterviewSocket(total_questions=2)

app = FastAPI(title="Intervux-AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@app.websocket("/ws/interview")
async def websocket_interview(ws: WebSocket):
    await interview_socket.handle(ws)


@app.on_event("shutdown")
async def on_shutdown():
    await interview_socket.shutdown()
