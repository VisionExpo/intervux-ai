import asyncio
import json

import pytest


class AtomicScriptRedis:
    """Small Redis script double with atomic eval semantics for registry tests."""

    def __init__(self):
        self.values = {}
        self.sets = {}
        self.lock = asyncio.Lock()
        self.fail_next_eval = False

    async def eval(self, script, numkeys, *args):
        if self.fail_next_eval:
            self.fail_next_eval = False
            raise ConnectionError("simulated Redis failure")

        async with self.lock:
            if "-- REGISTER_SESSION" in script:
                metadata_key, index_key, payload, _ttl, session_id = args
                self.values[metadata_key] = payload
                self.sets.setdefault(index_key, set()).add(session_id)
                return 1

            if "-- BEGIN_CLAIM" in script:
                metadata_key, index_key, payload, _ttl, generation, claim_id, session_id = args
                current_raw = self.values.get(metadata_key)
                if current_raw:
                    current = json.loads(current_raw)
                    current_generation = current.get("generation", -1)
                    if current_generation > generation:
                        return 0
                    if current_generation == generation and current.get("claim_id") != claim_id:
                        return 0
                self.values[metadata_key] = payload
                self.sets.setdefault(index_key, set()).add(session_id)
                return 1

            if "-- ACTIVATE_CLAIM" in script:
                metadata_key, claim_id, generation, socket_id, _ttl = args
                raw = self.values.get(metadata_key)
                if not raw:
                    return 0
                metadata = json.loads(raw)
                if (
                    metadata.get("claim_id") != claim_id
                    or metadata.get("generation") != generation
                    or metadata.get("socket_id") != socket_id
                    or metadata.get("lifecycle_state") != "claiming"
                ):
                    return 0
                metadata["lifecycle_state"] = "active"
                self.values[metadata_key] = json.dumps(metadata)
                return 1

            if "-- RENEW_CLAIM" in script:
                metadata_key, socket_id, generation, claim_id, _ttl = args
                raw = self.values.get(metadata_key)
                if not raw:
                    return 0
                metadata = json.loads(raw)
                if (
                    metadata.get("socket_id") != socket_id
                    or metadata.get("generation") != generation
                    or metadata.get("claim_id") != claim_id
                    or metadata.get("lifecycle_state") != "active"
                ):
                    return 0
                return 1

            if "-- UNREGISTER_SESSION" in script:
                metadata_key, index_key, socket_id, generation, claim_id, session_id = args
                raw = self.values.get(metadata_key)
                if raw is None:
                    return 0
                metadata = json.loads(raw)
                if metadata.get("socket_id") != socket_id:
                    return 0
                if generation != "" and metadata.get("generation") != generation:
                    return 0
                if claim_id != "" and metadata.get("claim_id") != claim_id:
                    return 0
                del self.values[metadata_key]
                self.sets.setdefault(index_key, set()).discard(session_id)
                return 1

            if "-- COUNT_SESSIONS" in script:
                (index_key, prefix) = args
                members = self.sets.setdefault(index_key, set())
                for session_id in list(members):
                    raw = self.values.get(f"{prefix}{session_id}")
                    try:
                        metadata = json.loads(raw) if raw is not None else None
                    except (TypeError, json.JSONDecodeError):
                        metadata = None
                    if not metadata or not metadata.get("socket_id"):
                        members.discard(session_id)
                return len(members)

            if "-- SAVE_STATE_IF_OWNER" in script:
                metadata_key, state_key, socket_id, payload, _ttl, generation, claim_id = args
                raw = self.values.get(metadata_key)
                if raw is None or json.loads(raw).get("socket_id") != socket_id:
                    return 0
                metadata = json.loads(raw)
                if generation != "" and (metadata.get("generation") != generation or metadata.get("lifecycle_state") != "active"):
                    return 0
                if claim_id != "" and metadata.get("claim_id") != claim_id:
                    return 0
                self.values[state_key] = payload
                return 1

            if "-- CLEAR_STATE_IF_OWNER" in script:
                metadata_key, *rest = args
                state_keys = rest[:4]
                socket_id, generation, claim_id = rest[4:]
                raw = self.values.get(metadata_key)
                if raw is None or json.loads(raw).get("socket_id") != socket_id:
                    return -1
                metadata = json.loads(raw)
                if generation != "" and (metadata.get("generation") != generation or metadata.get("lifecycle_state") != "active"):
                    return -1
                if claim_id != "" and metadata.get("claim_id") != claim_id:
                    return -1
                removed = 0
                for key in state_keys:
                    removed += int(self.values.pop(key, None) is not None)
                return removed

            raise AssertionError(f"Unexpected Redis script: {script}")

    async def get(self, key):
        return self.values.get(key)

    async def sadd(self, key, value):
        members = self.sets.setdefault(key, set())
        before = len(members)
        members.add(value)
        return len(members) - before

    async def scan_iter(self, pattern):
        assert pattern == "session:*"
        for key in list(self.values):
            if key.startswith("session:"):
                yield key


@pytest.fixture
def redis_double(monkeypatch):
    import backend.modules.interview.sessions.registry as registry_module

    fake = AtomicScriptRedis()
    monkeypatch.setattr(registry_module.redis, "from_url", lambda *_args, **_kwargs: fake)
    return fake


@pytest.mark.asyncio
async def test_registry_registration_replacement_and_unregistration_are_idempotent(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    first = {"user_id": "candidate-1", "socket_id": "socket-a"}
    replacement = {"user_id": "candidate-1", "socket_id": "socket-b"}

    assert await registry.register("session-1", first) is True
    assert await registry.count() == 1
    assert await registry.register("session-1", first) is True
    assert await registry.count() == 1

    assert await registry.register("session-1", replacement) is True
    assert await registry.count() == 1
    assert await registry.owns_session("session-1", "socket-b", "candidate-1") is True
    assert await registry.unregister("session-1", expected_socket_id="socket-a") is False
    assert await registry.count() == 1

    assert await registry.unregister("session-1", expected_socket_id="socket-b") is True
    assert await registry.count() == 0
    assert await registry.unregister("session-1", expected_socket_id="socket-b") is False
    assert await registry.count() == 0


@pytest.mark.asyncio
async def test_concurrent_same_id_register_and_unregister_preserve_replacement(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    assert await registry.register("session-race", {"user_id": "u", "socket_id": "old"})

    await asyncio.gather(
        registry.register("session-race", {"user_id": "u", "socket_id": "new"}),
        registry.unregister("session-race", expected_socket_id="old"),
    )

    metadata = await registry.get_metadata("session-race")
    assert metadata is not None
    assert metadata["socket_id"] == "new"
    assert await registry.count() == 1
    assert await registry.unregister("session-race", expected_socket_id="new") is True
    assert await registry.count() == 0


@pytest.mark.asyncio
async def test_registry_count_prunes_expired_metadata(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    assert await registry.register("live", {"user_id": "u", "socket_id": "live-socket"})
    assert await registry.register("expired", {"user_id": "u", "socket_id": "expired-socket"})
    redis_double.values.pop("session:expired")

    assert await registry.cleanup_stale_sessions() == 1
    assert redis_double.sets["session_active_ids"] == {"live"}


@pytest.mark.asyncio
async def test_registry_count_backfills_live_entries_from_legacy_metadata(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    redis_double.values["session:legacy"] = json.dumps(
        {"user_id": "u", "socket_id": "legacy-socket"}
    )
    redis_double.values["session_cluster_count"] = "27"
    registry = RedisSessionRegistry()

    assert await registry.count() == 1
    assert redis_double.sets["session_active_ids"] == {"legacy"}


@pytest.mark.asyncio
async def test_registry_redis_errors_do_not_report_success(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    redis_double.fail_next_eval = True
    assert await registry.register("session-error", {"user_id": "u", "socket_id": "s"}) is False
    assert await registry.count() == 0

    assert await registry.register("session-error", {"user_id": "u", "socket_id": "s"}) is True
    redis_double.fail_next_eval = True
    assert await registry.unregister("session-error", expected_socket_id="s") is False
    assert await registry.owns_session("session-error", "s", "u") is True


@pytest.mark.asyncio
async def test_state_save_and_cleanup_are_fenced_by_current_socket(redis_double, monkeypatch):
    import backend.services.redis_manager as redis_module
    from backend.modules.interview.models import InterviewState

    monkeypatch.setattr(redis_module.redis, "from_url", lambda *_args, **_kwargs: redis_double)
    manager = redis_module.RedisManager()
    redis_double.values["session:session-state"] = json.dumps(
        {"user_id": "u", "socket_id": "replacement"}
    )
    state = InterviewState(user_id="u", session_id="session-state")

    assert await manager.save_session_state_obj(
        "session-state", (state, {}), expected_socket_id="stale"
    ) is False
    assert "interview:state_obj:session-state" not in redis_double.values

    assert await manager.save_session_state_obj(
        "session-state", (state, {}), expected_socket_id="replacement"
    ) is True
    assert await manager.clear_session_state_obj_if_owner("session-state", "stale") is False
    assert "interview:state_obj:session-state" in redis_double.values
    assert await manager.clear_session_state_obj_if_owner("session-state", "replacement") is True
    assert "interview:state_obj:session-state" not in redis_double.values


@pytest.mark.asyncio
async def test_claim_mirror_requires_exact_claim_to_activate_and_unregister(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    claim = {
        "user_id": "candidate-1",
        "socket_id": "socket-new",
        "generation": 8,
        "claim_id": "claim-8",
    }
    assert await registry.begin_claim("claim-session", claim) is True
    assert await registry.owns_session(
        "claim-session", "socket-new", generation=8, claim_id="claim-8"
    ) is False
    assert await registry.activate_claim("claim-session", "socket-new", 7, "claim-7") is False
    assert await registry.activate_claim("claim-session", "socket-new", 8, "claim-8") is True
    assert await registry.owns_session(
        "claim-session", "socket-new", generation=8, claim_id="claim-8"
    ) is True
    assert await registry.unregister(
        "claim-session", "socket-new", generation=7, claim_id="claim-7"
    ) is False
    assert await registry.renew_claim("claim-session", "socket-new", 7, "claim-7") is False
    assert await registry.renew_claim("claim-session", "socket-new", 8, "claim-8") is True
    assert await registry.owns_session(
        "claim-session", "socket-new", generation=8, claim_id="claim-8"
    ) is True


@pytest.mark.asyncio
async def test_claim_mirror_failures_remain_unowned(redis_double):
    from backend.modules.interview.sessions.registry import RedisSessionRegistry

    registry = RedisSessionRegistry()
    redis_double.fail_next_eval = True
    claim = {"user_id": "u", "socket_id": "s", "generation": 1, "claim_id": "c1"}
    assert await registry.begin_claim("claim-failure", claim) is False
    assert await registry.get_metadata("claim-failure") is None

    assert await registry.begin_claim("claim-failure", claim) is True
    redis_double.fail_next_eval = True
    assert await registry.activate_claim("claim-failure", "s", 1, "c1") is False
    assert await registry.owns_session("claim-failure", "s", generation=1, claim_id="c1") is False
