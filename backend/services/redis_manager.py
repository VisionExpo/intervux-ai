import json
import os
import pickle
import redis.asyncio as redis
from typing import Any, Dict, Optional, AsyncGenerator

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_SAVE_STATE_IF_OWNER = """
-- SAVE_STATE_IF_OWNER
local raw = redis.call('GET', KEYS[1])
if not raw then return 0 end
local ok, metadata = pcall(cjson.decode, raw)
if not ok or metadata.socket_id ~= ARGV[1] then return 0 end
if ARGV[4] ~= '' and metadata.lifecycle_state ~= 'active' then return 0 end
if ARGV[4] ~= '' and tonumber(metadata.generation or -1) ~= tonumber(ARGV[4]) then return 0 end
if ARGV[5] ~= '' and metadata.claim_id ~= ARGV[5] then return 0 end
redis.call('SET', KEYS[2], ARGV[2], 'EX', ARGV[3])
return 1
"""

_CLEAR_STATE_IF_OWNER = """
-- CLEAR_STATE_IF_OWNER
local raw = redis.call('GET', KEYS[1])
if not raw then return -1 end
local ok, metadata = pcall(cjson.decode, raw)
if not ok or metadata.socket_id ~= ARGV[1] then return -1 end
if ARGV[2] ~= '' and metadata.lifecycle_state ~= 'active' then return -1 end
if ARGV[2] ~= '' and tonumber(metadata.generation or -1) ~= tonumber(ARGV[2]) then return -1 end
if ARGV[3] ~= '' and metadata.claim_id ~= ARGV[3] then return -1 end
return redis.call('DEL', KEYS[2], KEYS[3], KEYS[4], KEYS[5])
"""

class RedisManager:
    def __init__(self):
        # We store connection securely
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self.redis_bin = redis.from_url(REDIS_URL, decode_responses=False)

    async def save_session_state_obj(
        self,
        session_id: str,
        state_obj: Any,
        expected_socket_id: str,
        generation: int | None = None,
        claim_id: str | None = None,
        expire_seconds: int = 7200,
    ) -> bool:
        if isinstance(state_obj, tuple) and len(state_obj) == 2:
            state, cache = state_obj
            data = {
                "state": state.to_dict(),
                "cache": cache
            }
            saved = await self.redis.eval(
                _SAVE_STATE_IF_OWNER,
                2,
                f"session:{session_id}",
                f"interview:state_obj:{session_id}",
                expected_socket_id,
                json.dumps(data),
                expire_seconds,
                "" if generation is None else generation,
                "" if claim_id is None else claim_id,
            )
            return saved == 1
        return False

    async def clear_session_state_obj_if_owner(
        self,
        session_id: str,
        expected_socket_id: str,
        generation: int | None = None,
        claim_id: str | None = None,
    ) -> bool:
        """Delete session snapshots only while the given socket still owns the ID."""
        deleted = await self.redis.eval(
            _CLEAR_STATE_IF_OWNER,
            5,
            f"session:{session_id}",
            f"interview:state_obj:{session_id}",
            f"interview:state:{session_id}",
            f"interview:cache:{session_id}",
            f"interview:results:{session_id}",
            expected_socket_id,
            "" if generation is None else generation,
            "" if claim_id is None else claim_id,
        )
        return deleted >= 0

    async def get_session_state_obj(self, session_id: str) -> Optional[Any]:
        data = await self.redis.get(f"interview:state_obj:{session_id}")
        if data:
            try:
                parsed = json.loads(data)
                from backend.modules.interview.models import InterviewState
                state = InterviewState.from_dict(parsed.get("state", {}))
                cache = parsed.get("cache", {})
                return (state, cache)
            except Exception:
                return None
        return None

    async def save_session_state(self, session_id: str, state_data: Dict[str, Any], expire_seconds: int = 3600):
        await self.redis.set(f"interview:state:{session_id}", json.dumps(state_data), ex=expire_seconds)

    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        data = await self.redis.get(f"interview:state:{session_id}")
        return json.loads(data) if data else None

    async def clear_session_state(self, session_id: str):
        await self.redis.delete(f"interview:state:{session_id}")

    async def save_cache(self, session_id: str, cache_data: Dict[str, Any], expire_seconds: int = 3600):
        await self.redis.set(f"interview:cache:{session_id}", json.dumps(cache_data), ex=expire_seconds)

    async def get_cache(self, session_id: str) -> Optional[Dict[str, Any]]:
        data = await self.redis.get(f"interview:cache:{session_id}")
        return json.loads(data) if data else None

    async def clear_cache(self, session_id: str):
        await self.redis.delete(f"interview:cache:{session_id}")

    async def publish(self, channel: str, message: Dict[str, Any]):
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str) -> AsyncGenerator[Dict[str, Any], None]:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        # Using async for directly over listen() which is a supported pattern in redis-py async
        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    yield json.loads(message["data"])
                except Exception:
                    pass

redis_client = RedisManager()
