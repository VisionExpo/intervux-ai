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

ACTIVE_CLAIM_TTL_SECONDS = 120

_REGISTER_SESSION = """
-- REGISTER_SESSION
local index_type = redis.call('TYPE', KEYS[2]).ok
if index_type ~= 'none' and index_type ~= 'set' then
    return redis.error_reply('session index has an unexpected type')
end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
redis.call('SADD', KEYS[2], ARGV[3])
return 1
"""

_UNREGISTER_SESSION = """
-- UNREGISTER_SESSION
local index_type = redis.call('TYPE', KEYS[2]).ok
if index_type ~= 'none' and index_type ~= 'set' then
    return redis.error_reply('session index has an unexpected type')
end
local raw = redis.call('GET', KEYS[1])
if not raw then return 0 end
local ok, metadata = pcall(cjson.decode, raw)
if not ok or metadata.socket_id ~= ARGV[1] then return 0 end
if ARGV[2] ~= '' and tonumber(metadata.generation or -1) ~= tonumber(ARGV[2]) then return 0 end
if ARGV[3] ~= '' and metadata.claim_id ~= ARGV[3] then return 0 end
redis.call('DEL', KEYS[1])
redis.call('SREM', KEYS[2], ARGV[4])
return 1
"""

_BEGIN_CLAIM = """
-- BEGIN_CLAIM: SQL has already fenced the previous generation.
local raw = redis.call('GET', KEYS[1])
if raw then
    local ok, current = pcall(cjson.decode, raw)
    if not ok or type(current) ~= 'table' then return 0 end
    local current_generation = tonumber(current.generation or -1)
    local next_generation = tonumber(ARGV[3])
    if current_generation > next_generation then return 0 end
    if current_generation == next_generation and current.claim_id ~= ARGV[4] then return 0 end
end
local index_type = redis.call('TYPE', KEYS[2]).ok
if index_type ~= 'none' and index_type ~= 'set' then
    return redis.error_reply('session index has an unexpected type')
end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
redis.call('SADD', KEYS[2], ARGV[5])
return 1
"""

_ACTIVATE_CLAIM = """
-- ACTIVATE_CLAIM
local raw = redis.call('GET', KEYS[1])
if not raw then return 0 end
local ok, metadata = pcall(cjson.decode, raw)
if not ok or metadata.claim_id ~= ARGV[1]
    or tonumber(metadata.generation or -1) ~= tonumber(ARGV[2])
    or metadata.socket_id ~= ARGV[3]
    or metadata.lifecycle_state ~= 'claiming' then return 0 end
metadata.lifecycle_state = 'active'
redis.call('SET', KEYS[1], cjson.encode(metadata), 'EX', ARGV[4])
return 1
"""

_RENEW_CLAIM = """
-- RENEW_CLAIM
local raw = redis.call('GET', KEYS[1])
if not raw then return 0 end
local ok, metadata = pcall(cjson.decode, raw)
if not ok or metadata.lifecycle_state ~= 'active'
    or metadata.socket_id ~= ARGV[1]
    or tonumber(metadata.generation or -1) ~= tonumber(ARGV[2])
    or metadata.claim_id ~= ARGV[3] then return 0 end
redis.call('EXPIRE', KEYS[1], ARGV[4])
return 1
"""

_COUNT_SESSIONS = """
-- COUNT_SESSIONS
local index_type = redis.call('TYPE', KEYS[1]).ok
if index_type ~= 'none' and index_type ~= 'set' then
    return redis.error_reply('session index has an unexpected type')
end
local members = redis.call('SMEMBERS', KEYS[1])
for _, session_id in ipairs(members) do
    local raw = redis.call('GET', ARGV[1] .. session_id)
    local ok, metadata = pcall(cjson.decode, raw or '')
    if not raw or not ok or type(metadata) ~= 'table' or not metadata.socket_id then
        redis.call('SREM', KEYS[1], session_id)
    end
end
return redis.call('SCARD', KEYS[1])
"""

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisSessionRegistry:
    """
    Stateless Global registry using Redis to manage active interview sessions.
    Provides cluster-safe session tracking.
    """

    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self._active_sessions_key = "session_active_ids"
        self._active_index_initialized = False

    async def _initialize_active_index(self) -> None:
        """Backfill live registry entries left by a pre-index deployment."""
        if self._active_index_initialized:
            return

        async for key in self.redis.scan_iter("session:*"):
            if key == "session_cluster_count":
                continue
            raw = await self.redis.get(key)
            try:
                metadata = json.loads(raw) if raw else None
            except (TypeError, json.JSONDecodeError):
                metadata = None
            if isinstance(metadata, dict) and metadata.get("socket_id"):
                session_id = key.removeprefix("session:")
                await self.redis.sadd(self._active_sessions_key, session_id)

        self._active_index_initialized = True

    async def register(self, session_id: str, payload: dict) -> bool:
        """Atomically replace metadata and index the session exactly once."""
        try:
            registered = await self.redis.eval(
                _REGISTER_SESSION,
                2,
                f"session:{session_id}",
                self._active_sessions_key,
                json.dumps(payload),
                10800,
                session_id,
            )
            if registered != 1:
                return False
            logger.info("Session registered to Redis", extra={"extra_data": {"session_id": session_id}})
            return True
        except Exception as e:
            logger.error(f"Redis register error: {e}")
            return False

    async def begin_claim(self, session_id: str, payload: dict) -> bool:
        """Mirror a SQL-winning claim as pending; no socket owns it yet."""
        try:
            generation = int(payload["generation"])
            claim_id = str(payload["claim_id"])
            pending = {**payload, "lifecycle_state": "claiming"}
            result = await self.redis.eval(
                _BEGIN_CLAIM,
                2,
                f"session:{session_id}",
                self._active_sessions_key,
                json.dumps(pending),
                int(payload.get("claim_ttl_seconds", 40)),
                generation,
                claim_id,
                session_id,
            )
            return result == 1
        except Exception:
            logger.exception("Redis pending claim mirror failed")
            return False

    async def activate_claim(
        self, session_id: str, socket_id: str, generation: int, claim_id: str
    ) -> bool:
        """Promote only the exact pending SQL claim to Redis active."""
        try:
            return await self.redis.eval(
                _ACTIVATE_CLAIM,
                1,
                f"session:{session_id}",
                claim_id,
                generation,
                socket_id,
                ACTIVE_CLAIM_TTL_SECONDS,
            ) == 1
        except Exception:
            logger.exception("Redis claim activation failed")
            return False

    async def renew_claim(self, session_id: str, socket_id: str, generation: int, claim_id: str) -> bool:
        """Bound stale active registry/accounting entries after worker loss."""
        try:
            return await self.redis.eval(
                _RENEW_CLAIM,
                1,
                f"session:{session_id}",
                socket_id,
                generation,
                claim_id,
                ACTIVE_CLAIM_TTL_SECONDS,
            ) == 1
        except Exception:
            logger.exception("Redis owner lease renewal failed")
            return False

    async def unregister(
        self,
        session_id: str,
        expected_socket_id: str,
        generation: int | None = None,
        claim_id: str | None = None,
    ) -> bool:
        """Remove a registry entry only if this socket still owns it."""
        try:
            deleted = await self.redis.eval(
                _UNREGISTER_SESSION,
                2,
                f"session:{session_id}",
                self._active_sessions_key,
                expected_socket_id,
                "" if generation is None else generation,
                "" if claim_id is None else claim_id,
                session_id,
            )
            if deleted == 1:
                logger.info("Session unregistered from Redis", extra={"extra_data": {"session_id": session_id}})
                return True
            return False
        except Exception as e:
            logger.error(f"Redis unregister error: {e}")
            return False

    async def get_metadata(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state from Redis."""
        try:
            data = await self.redis.get(f"session:{session_id}")
            return json.loads(data) if data else None
        except Exception:
            return None

    async def owns_session(
        self,
        session_id: str,
        socket_id: str,
        user_id: Optional[str] = None,
        generation: int | None = None,
        claim_id: str | None = None,
    ) -> bool:
        """Check that the registered socket and principal match this session object."""
        metadata = await self.get_metadata(session_id)
        return bool(
            metadata
            and metadata.get("socket_id") == socket_id
            and (user_id is None or metadata.get("user_id") == user_id)
            and (generation is None or metadata.get("generation") == generation)
            and (claim_id is None or metadata.get("claim_id") == claim_id)
            and (generation is None or metadata.get("lifecycle_state") == "active")
        )

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
        """Return indexed sessions with live metadata, pruning expired entries atomically."""
        try:
            await self._initialize_active_index()
            return int(await self.redis.eval(
                _COUNT_SESSIONS,
                1,
                self._active_sessions_key,
                "session:",
            ))
        except Exception:
            logger.exception("Redis session count failed")
            raise

    async def save_state(self, session_id: str, payload: dict) -> None:
        """Save mid-interview state to Redis."""
        try:
            await self.redis.setex(f"session:{session_id}", 10800, json.dumps(payload))
        except Exception as e:
            logger.error(f"Redis save_state error: {e}")

    async def cleanup_stale_sessions(self) -> int:
        """
        Reconcile the active ID index with live session metadata.

        Returns the corrected count. Expired metadata is pruned by the same
        atomic operation used by count().
        """
        try:
            actual = await self.count()
            logger.info(
                "Reconciled stale session index",
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
