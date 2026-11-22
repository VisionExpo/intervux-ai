"""Cross-store claim tests; require a dedicated real PostgreSQL and Redis DB."""

import asyncio
import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.infrastructure.database.database import Base
from backend.models.candidate_portal import CandidateProfile, MockInterview
from backend.modules.interview.persistence import claim_mock_interview_connection
from backend.modules.interview.sessions.registry import RedisSessionRegistry
from backend.services.redis_manager import RedisManager


PG_URL = os.getenv("OWNERSHIP_TEST_DATABASE_URL", "")
REDIS_URL = os.getenv("OWNERSHIP_TEST_REDIS_URL", "")
pytestmark = [
    pytest.mark.integration,
    # The module-scoped engine/Redis clients must share the tests' event loop;
    # asyncpg connections cannot cross loops.
    pytest.mark.asyncio(loop_scope="module"),
    pytest.mark.skipif(
        not PG_URL.startswith(("postgresql://", "postgresql+asyncpg://")) or not REDIS_URL,
        reason="requires dedicated OWNERSHIP_TEST_DATABASE_URL (PostgreSQL) and OWNERSHIP_TEST_REDIS_URL",
    ),
]


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def stores():
    pg_url = PG_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(pg_url, pool_pre_ping=True)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    redis_client = RedisManager.__new__(RedisManager)
    import redis.asyncio as redis

    redis_client.redis = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.redis_bin = redis.from_url(REDIS_URL, decode_responses=False)
    registry = RedisSessionRegistry.__new__(RedisSessionRegistry)
    registry.redis = redis.from_url(REDIS_URL, decode_responses=True)
    registry._active_sessions_key = "session_active_ids"
    registry._active_index_initialized = True

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield sessions, registry, redis_client
    await registry.redis.aclose()
    await redis_client.redis.aclose()
    await redis_client.redis_bin.aclose()
    await engine.dispose()


async def _create_row(sessions):
    user_id = f"ownership-{uuid.uuid4().hex}"
    session_id = f"mock-{uuid.uuid4().hex}"
    profile_id = None
    async with sessions() as db:
        profile = CandidateProfile(user_id=user_id, name="Ownership Integration", mock_interviews_remaining=3)
        db.add(profile)
        await db.flush()
        profile_id = profile.id
        db.add(MockInterview(candidate_id=profile.id, session_id=session_id, status="in_progress", interview_number=1))
        await db.commit()
    return user_id, session_id, profile_id


@pytest.mark.asyncio(loop_scope="module")
async def test_real_postgres_redis_claim_race_has_one_owner(stores):
    sessions, registry, redis_manager = stores
    user_id, session_id, _profile_id = await _create_row(sessions)

    async def attempt(socket_id):
        async with sessions() as db:
            return await claim_mock_interview_connection(
                session_id, user_id, socket_id, registry=registry, db=db
            )

    claims = await asyncio.gather(attempt("socket-a"), attempt("socket-b"))
    winners = [claim for claim in claims if claim]
    assert len(winners) == 1
    winner = winners[0]
    owner = "socket-a" if winner["socket_id"] == "socket-a" else "socket-b"
    assert await registry.owns_session(
        session_id,
        owner,
        user_id,
        generation=winner["generation"],
        claim_id=winner["claim_id"],
    )

    from backend.modules.interview.models import InterviewState

    state = InterviewState(user_id=user_id, session_id=session_id)
    assert await redis_manager.save_session_state_obj(
        session_id,
        (state, {}),
        owner,
        generation=winner["generation"],
        claim_id=winner["claim_id"],
    )
    assert await redis_manager.save_session_state_obj(
        session_id,
        (state, {}),
        "stale-socket",
        generation=winner["generation"] - 1,
        claim_id="stale-claim",
    ) is False
    assert await registry.unregister(
        session_id,
        "stale-socket",
        generation=winner["generation"] - 1,
        claim_id="stale-claim",
    ) is False


@pytest.mark.asyncio(loop_scope="module")
async def test_real_postgres_completion_and_reconnect_have_one_winner(stores, monkeypatch):
    from sqlalchemy import select

    from backend.models.candidate_portal import CandidateProfile, MockInterview
    from backend.modules.interview import persistence

    sessions, registry, _redis_manager = stores
    user_id, session_id, profile_id = await _create_row(sessions)
    async with sessions() as db:
        old = await claim_mock_interview_connection(
            session_id, user_id, "socket-old", registry=registry, db=db
        )
    assert old is not None
    monkeypatch.setattr(
        "backend.modules.interview.sessions.registry.get_session_registry",
        lambda: registry,
    )

    async def reconnect():
        async with sessions() as db:
            return await claim_mock_interview_connection(
                session_id, user_id, "socket-new", registry=registry, db=db
            )

    async def complete():
        async with sessions() as db:
            return await persistence.complete_mock_interview(
                session_id,
                {"summary": "report"},
                [],
                db=db,
                expected_socket_id="socket-old",
                expected_generation=old["generation"],
                expected_claim_id=old["claim_id"],
            )

    reconnect_result, completion_result = await asyncio.gather(reconnect(), complete())
    assert bool(reconnect_result) != bool(completion_result)
    async with sessions() as db:
        interview = (await db.execute(
            select(MockInterview).where(MockInterview.session_id == session_id)
        )).scalar_one()
        profile = (await db.execute(
            select(CandidateProfile).where(CandidateProfile.id == profile_id)
        )).scalar_one()
        if interview.status == "completed":
            assert completion_result is True
            assert reconnect_result is None
            assert profile.mock_interviews_remaining == 2
        else:
            assert interview.status == "in_progress"
            assert completion_result is False
            assert reconnect_result is not None
            assert profile.mock_interviews_remaining == 3
