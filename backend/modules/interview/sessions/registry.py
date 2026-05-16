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

    async def get_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state from Redis."""
        try:
            data = await self.redis.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception:
            return None

    async def find_active_session_by_user(self, user_id: str) -> Optional[str]:
        """
        Return an active session_id for a given user_id if one exists.
        """
        try:
            async for key in self.redis.scan_iter("session:*"):
                if key == "session_cluster_count":
                    continue
                raw = await self.redis.get(key)
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                except Exception:
                    continue
                if payload.get("user_id") == user_id:
                    return key.split("session:", 1)[1]
        except Exception as e:
            logger.error(f"find_active_session_by_user error: {e}")
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

    async def cleanup_stale_sessions(self) -> int:
        """
        Reconcile session_cluster_count with actual session:* keys.

        Returns the corrected count.  This prevents the counter from
        drifting when a node crashes without calling unregister().
        """
        try:
            keys = []
            async for key in self.redis.scan_iter("session:*"):
                keys.append(key)

            # Exclude the counter key itself
            actual = len([k for k in keys if k != "session_cluster_count"])
            await self.redis.set("session_cluster_count", actual)
            logger.info(
                "Reconciled stale session count",
                extra={"extra_data": {"actual_count": actual}},
            )
            return actual
        except Exception as e:
            logger.error(f"cleanup_stale_sessions error: {e}")
            return 0

    async def clear_all_session_keys(self, session_id: str) -> None:
        """
        Delete ALL Redis keys associated with a specific session.

        Useful for full session purge on abnormal shutdown.
        """
        prefixes = [
            f"session:{session_id}",
            f"interview:state:{session_id}",
            f"interview:state_obj:{session_id}",
            f"interview:cache:{session_id}",
            f"interview:results:{session_id}",
        ]
        try:
            await self.redis.delete(*prefixes)
        except Exception as e:
            logger.error(f"clear_all_session_keys error: {e}")

_registry: Optional[RedisSessionRegistry] = None

def get_session_registry() -> RedisSessionRegistry:
    """Get the global stateless session registry."""
    global _registry
    if _registry is None:
        _registry = RedisSessionRegistry()
    return _registry
