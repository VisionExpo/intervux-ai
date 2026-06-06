import json
import os
import pickle
import redis.asyncio as redis
from typing import Any, Dict, Optional, AsyncGenerator

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class RedisManager:
    def __init__(self):
        # We store connection securely
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)
        self.redis_bin = redis.from_url(REDIS_URL, decode_responses=False)

    async def save_session_state_obj(self, session_id: str, state_obj: Any, expire_seconds: int = 7200):
        if isinstance(state_obj, tuple) and len(state_obj) == 2:
            state, cache = state_obj
            data = {
                "state": state.to_dict(),
                "cache": cache
            }
            await self.redis.set(f"interview:state_obj:{session_id}", json.dumps(data), ex=expire_seconds)

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
