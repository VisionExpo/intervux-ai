import time
import json
import asyncio
from typing import Dict, Any, Optional
from backend.services.redis_manager import redis_client
from backend.core.logging.structured_logger import logger
from backend.core.exceptions.types import IntervuxSystemError

class SessionTelemetry:
    TTL_SECONDS = 7 * 24 * 3600  # 7 days
    
    @classmethod
    def record(
        cls, 
        session_id: str, 
        event_type: str, 
        metadata: Dict[str, Any] = None, 
        error: Optional[IntervuxSystemError] = None,
        latency_ms: Optional[float] = None,
        **kwargs
    ):
        """Synchronous non-blocking telemetry emission."""
        try:
            socket_id = kwargs.pop("socket_id", None)
            seq = kwargs.pop("seq", None)

            full_metadata = (metadata or {}).copy()
            for k, v in kwargs.items():
                full_metadata[k] = v

            event = {
                "timestamp": time.time(),
                "event_type": event_type,
                "severity": getattr(error, "severity", "ERROR") if error else "INFO",
                "session_id": session_id,
                "metadata": full_metadata,
                "latency_ms": latency_ms
            }
            if socket_id is not None:
                event["socket_id"] = socket_id
            if seq is not None:
                event["seq"] = seq

            if error:
                event["error_detail"] = getattr(error, "message", str(error))
                event["retryable"] = getattr(error, "retryable", False)

            # Fire-and-forget to avoid blocking core loop
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(cls._flush_to_redis(session_id, event))
            except RuntimeError:
                pass

            # Log for stdout visibility
            severity = getattr(error, "severity", "ERROR") if error else "INFO"
            if severity in ["ERROR", "FATAL"]:
                logger.error(f"TELEMETRY: {event_type}", extra=event)
            else:
                logger.info(f"TELEMETRY: {event_type}", extra=event)

        except Exception as e:
            # Observability layer must never crash the system
            logger.error("Telemetry emission failed", extra={"error": str(e)})

    @classmethod
    async def record_event(
        cls, 
        session_id: str, 
        event_type: str, 
        metadata: Dict[str, Any] = None, 
        error: Optional[IntervuxSystemError] = None,
        latency_ms: Optional[float] = None,
        **kwargs
    ):
        """Async backward-compatible wrapper for record."""
        cls.record(
            session_id=session_id,
            event_type=event_type,
            metadata=metadata,
            error=error,
            latency_ms=latency_ms,
            **kwargs
        )
            
    @classmethod
    async def _flush_to_redis(cls, session_id: str, event: Dict[str, Any]):
        try:
            key = f"intervux:events:{session_id}"
            await redis_client.redis.rpush(key, json.dumps(event))
            # Set TTL on every push to be safe, but typically setting it once is better. 
            # Given it's a 7-day TTL, resetting it on push is fine.
            await redis_client.redis.expire(key, cls.TTL_SECONDS)
        except Exception:
            pass  # Fail safe

    @classmethod
    async def get_timeline(cls, session_id: str) -> list[Dict[str, Any]]:
        """Used by the Diagnostic API to reconstruct session flow."""
        try:
            key = f"intervux:events:{session_id}"
            raw_events = await redis_client.redis.lrange(key, 0, -1)
            return [json.loads(e) for e in raw_events]
        except Exception:
            return []
