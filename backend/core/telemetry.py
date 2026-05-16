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
    async def record_event(
        cls, 
        session_id: str, 
        event_type: str, 
        metadata: Dict[str, Any] = None, 
        error: Optional[IntervuxSystemError] = None,
        latency_ms: Optional[float] = None
    ):
        """Non-blocking telemetry emission."""
        try:
            event = {
                "timestamp": time.time(),
                "event_type": event_type,
                "severity": error.severity if error else "INFO",
                "session_id": session_id,
                "metadata": metadata or {},
                "latency_ms": latency_ms
            }
            
            if error:
                event["error_detail"] = error.message
                event["retryable"] = error.retryable
            
            # Fire-and-forget to avoid blocking core loop
            asyncio.create_task(cls._flush_to_redis(session_id, event))
            
            # Log for stdout visibility
            if error and error.severity in ["ERROR", "FATAL"]:
                logger.error(f"TELEMETRY: {event_type}", extra=event)
            else:
                logger.info(f"TELEMETRY: {event_type}", extra=event)
                
        except Exception as e:
            # Observability layer must never crash the system
            logger.error("Telemetry emission failed", extra={"error": str(e)})
            
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
