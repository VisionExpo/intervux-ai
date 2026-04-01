"""
Session Registry - Stateless Redis registry for managing active interview sessions.
"""

import os
import json
import logging
import redis.asyncio as redis
from typing import Dict, Optional, Any

from backend.core.logging.logger import get_logger

logger = get_logger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisSessionRegistry:
    """
    Stateless Global registry using Redis to manage active interview sessions.
    Provides cluster-safe session tracking.
    """

    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def register(self, session_id: str, payload: dict) -> None:
        """Register a new session to Redis."""
        try:
            # 3 hours max TTL for stray sessions
            await self.redis.setex(f"session:{session_id}", 10800, json.dumps(payload))
            await self.redis.incr("session_cluster_count")
            count = await self.count()
            logger.info("Session registered to Redis", extra={"extra_data": {"session_id": session_id, "active_count": count}})
        except Exception as e:
            logger.error(f"Redis register error: {e}")

    async def unregister(self, session_id: str) -> None:
        """Remove a session from Redis."""
        try:
            deleted = await self.redis.delete(f"session:{session_id}")
            if deleted:
                await self.redis.decr("session_cluster_count")
                count = await self.count()
                logger.info("Session unregistered from Redis", extra={"extra_data": {"session_id": session_id, "active_count": count}})
        except Exception as e:
            logger.error(f"Redis unregister error: {e}")

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state from Redis."""
        try:
            data = await self.redis.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception:
            return None

    async def count(self) -> int:
        """Get number of active sessions globally."""
        try:
            count = await self.redis.get("session_cluster_count")
            return int(count) if count else 0
        except Exception:
            return 0

    async def save_state(self, session_id: str, payload: dict) -> None:
        """Save mid-interview state to Redis."""
        try:
            await self.redis.setex(f"session:{session_id}", 10800, json.dumps(payload))
        except Exception as e:
            logger.error(f"Redis save_state error: {e}")

_registry: Optional[RedisSessionRegistry] = None

def get_session_registry() -> RedisSessionRegistry:
    """Get the global stateless session registry."""
    global _registry
    if _registry is None:
        _registry = RedisSessionRegistry()
    return _registry
