"""
Interview Persistence Service (New Location)
===========================================

Writes live interview results back to the MockInterview table.
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from backend.infrastructure.database.database import AsyncSessionLocal
from backend.models.candidate_portal import CandidateProfile, MockInterview
from backend.core.logging.logger import get_logger

logger = get_logger(__name__)

# Bounded recovery window for a process that died while a claim was in flight.
# This is an internal lease, not the user-facing five-minute reconnect window.
CLAIM_LEASE_SECONDS = 30


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def acquire_mock_interview_claim(
    session_id: str,
    user_id: str,
    socket_id: str,
    db: AsyncSession | None = None,
    lease_seconds: int = CLAIM_LEASE_SECONDS,
) -> Dict[str, Any] | None:
    """CAS an eligible row into claiming and issue a new fencing generation."""
    from sqlalchemy import and_, func, select, update

    from backend.infrastructure.database.database import AsyncSessionLocal

    async def _run(session):
        try:
            db_now = (await session.execute(select(func.current_timestamp()))).scalar_one()
            if db_now.tzinfo is None:
                db_now = db_now.replace(tzinfo=timezone.utc)
            row_result = await session.execute(
                select(
                    MockInterview.id,
                    MockInterview.connection_state,
                    MockInterview.connection_generation,
                    MockInterview.claim_lease_until,
                )
                .join(CandidateProfile, MockInterview.candidate_id == CandidateProfile.id)
                .where(
                    MockInterview.session_id == session_id,
                    CandidateProfile.user_id == user_id,
                    MockInterview.status == "in_progress",
                )
            )
            row = row_result.one_or_none()
            if row is None:
                return None

            now = db_now
            old_state = row.connection_state or "unclaimed"
            old_generation = row.connection_generation or 0
            eligible = old_state in {"unclaimed", "active"} or (
                old_state == "claiming"
                and row.claim_lease_until is not None
                and (
                    row.claim_lease_until.replace(tzinfo=timezone.utc)
                    if row.claim_lease_until.tzinfo is None
                    else row.claim_lease_until
                ) <= now
            )
            if not eligible:
                return None

            new_generation = old_generation + 1
            new_claim_id = str(uuid.uuid4())
            lease_until = now + timedelta(seconds=max(1, min(int(lease_seconds), 120)))
            state_predicate = MockInterview.connection_state == old_state
            if old_state == "claiming":
                state_predicate = and_(
                    state_predicate,
                    MockInterview.claim_lease_until <= db_now,
                )
            claimed = await session.execute(
                update(MockInterview)
                .where(
                    MockInterview.id == row.id,
                    MockInterview.status == "in_progress",
                    MockInterview.connection_generation == old_generation,
                    state_predicate,
                )
                .values(
                    connection_state="claiming",
                    connection_generation=new_generation,
                    claim_id=new_claim_id,
                    claim_lease_until=lease_until,
                )
            )
            if claimed.rowcount != 1:
                await session.rollback()
                return None
            await session.commit()
            return {
                "generation": new_generation,
                "claim_id": new_claim_id,
                "lease_until": lease_until.isoformat(),
                "socket_id": socket_id,
                "previous_state": old_state,
            }
        except Exception:
            logger.exception("Could not acquire mock interview ownership claim")
            try:
                await session.rollback()
            except Exception:
                pass
            return None

    if db is not None:
        return await _run(db)
    async with AsyncSessionLocal() as session:
        return await _run(session)


async def activate_mock_interview_claim(
    session_id: str,
    generation: int,
    claim_id: str,
    db: AsyncSession | None = None,
) -> bool:
    """Finalize a claim only while its bounded SQL lease remains current."""
    from sqlalchemy import func, update
    from backend.infrastructure.database.database import AsyncSessionLocal

    async def _run(session):
        try:
            result = await session.execute(
                update(MockInterview)
                .where(
                    MockInterview.session_id == session_id,
                    MockInterview.status == "in_progress",
                    MockInterview.connection_state == "claiming",
                    MockInterview.connection_generation == generation,
                    MockInterview.claim_id == claim_id,
                    MockInterview.claim_lease_until > func.current_timestamp(),
                )
                .values(connection_state="active", claim_lease_until=None)
            )
            if result.rowcount != 1:
                await session.rollback()
                return False
            await session.commit()
            return True
        except Exception:
            logger.exception("Could not activate mock interview ownership claim")
            try:
                await session.rollback()
            except Exception:
                pass
            return False

    if db is not None:
        return await _run(db)
    async with AsyncSessionLocal() as session:
        return await _run(session)


async def claim_mock_interview_connection(
    session_id: str,
    user_id: str,
    socket_id: str,
    registry=None,
    db: AsyncSession | None = None,
) -> Dict[str, Any] | None:
    """Run SQL CAS → Redis pending → Redis active → SQL active in order.

    Any failed handoff leaves the SQL row non-active (or leaves the winning
    active row untouched), so callers must fail closed and allow lease recovery.
    """
    if registry is None:
        from backend.modules.interview.sessions.registry import get_session_registry

        registry = get_session_registry()

    claim = await acquire_mock_interview_claim(session_id, user_id, socket_id, db=db)
    if not claim:
        return None
    payload = {
        "user_id": user_id,
        "mock_id": session_id,
        "created_at": time.time(),
        "socket_id": socket_id,
        "generation": claim["generation"],
        "claim_id": claim["claim_id"],
        "claim_ttl_seconds": CLAIM_LEASE_SECONDS + 10,
    }
    if not await registry.begin_claim(session_id, payload):
        return None
    if not await registry.activate_claim(
        session_id, socket_id, claim["generation"], claim["claim_id"]
    ):
        return None
    if not await activate_mock_interview_claim(
        session_id, claim["generation"], claim["claim_id"], db=db
    ):
        return None
    return claim


async def owns_mock_interview_claim(
    session_id: str,
    user_id: str,
    socket_id: str,
    generation: int,
    claim_id: str,
    allow_completed: bool = False,
    allow_abandoned: bool = False,
    db: AsyncSession | None = None,
) -> bool:
    """Fail closed unless the SQL row still authorizes this exact socket epoch."""
    from sqlalchemy import select

    try:
        async def _check(session):
            result = await session.execute(
                select(MockInterview.id)
                .join(CandidateProfile, MockInterview.candidate_id == CandidateProfile.id)
                .where(
                    MockInterview.session_id == session_id,
                    CandidateProfile.user_id == user_id,
                    MockInterview.status.in_(
                        ["in_progress"]
                        + (["completed"] if allow_completed else [])
                        + (["abandoned"] if allow_abandoned else [])
                    ),
                    MockInterview.connection_state.in_(
                        ["active"]
                        + (["completed"] if allow_completed else [])
                        + (["abandoned"] if allow_abandoned else [])
                    ),
                    MockInterview.connection_generation == generation,
                    MockInterview.claim_id == claim_id,
                )
            )
            return result.scalar_one_or_none() is not None

        if db is not None:
            return await _check(db)
        async with AsyncSessionLocal() as session:
            return await _check(session)
    except Exception:
        logger.exception("Could not verify SQL interview ownership")
        return False


async def run_if_mock_interview_owner(
    session_id: str,
    user_id: str,
    generation: int,
    claim_id: str,
    effect,
    allow_completed: bool = False,
    allow_abandoned: bool = False,
) -> bool:
    """Hold the SQL ownership row lock through a Redis or WebSocket side effect.

    This gives claims and effectful operations a database ordering: an effect
    already holding the row completes before a new generation can fence it;
    once the new generation wins, the old effect cannot begin.
    """
    from sqlalchemy import select
    from backend.infrastructure.database.database import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as session:
            row = await session.execute(
                select(MockInterview.id)
                .join(CandidateProfile, MockInterview.candidate_id == CandidateProfile.id)
                .where(
                    MockInterview.session_id == session_id,
                    CandidateProfile.user_id == user_id,
                    MockInterview.status.in_(
                        ["in_progress"]
                        + (["completed"] if allow_completed else [])
                        + (["abandoned"] if allow_abandoned else [])
                    ),
                    MockInterview.connection_state.in_(
                        ["active"]
                        + (["completed"] if allow_completed else [])
                        + (["abandoned"] if allow_abandoned else [])
                    ),
                    MockInterview.connection_generation == generation,
                    MockInterview.claim_id == claim_id,
                )
                .with_for_update()
            )
            if row.scalar_one_or_none() is None:
                await session.rollback()
                return False
            result = await effect()
            if result is False:
                await session.rollback()
                return False
            await session.commit()
            return True
    except Exception:
        logger.exception("Fenced interview side effect failed")
        try:
            await session.rollback()
        except Exception:
            pass
        return False


async def can_access_mock_interview(session_id: str, user_id: str, role: str) -> bool:
    """Return whether a principal may connect to an in-progress mock interview.

    Mock interviews are created by the candidate-only start endpoint and are
    owned through MockInterview.candidate_id -> CandidateProfile.user_id.
    This deliberately does not infer recruiter access: MockInterview has no
    recruiter assignment relationship.
    """
    import re
    from sqlalchemy import select

    if role != "candidate" or not re.fullmatch(r"mock-[0-9a-f]{32}", session_id or ""):
        return False

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(MockInterview.status)
            .join(CandidateProfile, MockInterview.candidate_id == CandidateProfile.id)
            .where(
                MockInterview.session_id == session_id,
                CandidateProfile.user_id == user_id,
            )
        )
        status = result.scalar_one_or_none()
        return status == "in_progress"


def _add_dim(
    scores: dict,
    src_key: str,
    totals: Dict[str, float],
    counts: Dict[str, int],
    dest_key: str,
) -> None:
    val = scores.get(src_key)
    if val is not None:
        try:
            totals[dest_key] += float(val)
            counts[dest_key] += 1
        except Exception:
            pass


def _average_scores(answers: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute per-dimension averages across all evaluated answers.

    Returns keys: overall, technical, behavioral, reasoning in 0-100 scale.
    """
    totals: Dict[str, float] = {
        "overall": 0.0,
        "technical": 0.0,
        "behavioral": 0.0,
        "reasoning": 0.0,
    }
    counts: Dict[str, int] = {k: 0 for k in totals}

    for answer in answers:
        evaluation = answer.get("evaluation") or {}
        scores = evaluation.get("scores") or {}

        if not isinstance(scores, dict) or not scores:
            continue

        raw_values: List[float] = []
        for value in scores.values():
            try:
                raw_values.append(float(value))
            except Exception:
                continue

        if raw_values:
            overall_raw = scores.get("Overall")
            if overall_raw is None:
                overall_raw = sum(raw_values) / len(raw_values)
            try:
                totals["overall"] += float(overall_raw)
                counts["overall"] += 1
            except Exception:
                pass

        _add_dim(scores, "Technical", totals, counts, "technical")
        _add_dim(scores, "Behavioral", totals, counts, "behavioral")
        _add_dim(scores, "Reasoning", totals, counts, "reasoning")

        # Multipass evaluator variants
        _add_dim(scores, "Technical Accuracy", totals, counts, "technical")
        _add_dim(scores, "Depth", totals, counts, "technical")
        _add_dim(scores, "Clarity", totals, counts, "behavioral")
        _add_dim(scores, "Communication", totals, counts, "behavioral")

    result: Dict[str, float] = {}
    for key in totals:
        if counts[key]:
            avg_0_to_10 = totals[key] / counts[key]
            result[key] = round(min(avg_0_to_10 * 10.0, 100.0), 2)
        else:
            result[key] = 0.0

    return result


def _build_transcript(answers: List[Dict[str, Any]]) -> str:
    """Concatenate Q&A pairs into a readable transcript string."""
    lines: List[str] = []
    for i, answer in enumerate(answers, start=1):
        question = answer.get("question", "")
        reply = answer.get("answer", "")
        if question:
            lines.append(f"Q{i}: {question}")
        if reply:
            lines.append(f"A{i}: {reply}")
    return "\n".join(lines)


async def complete_mock_interview(
    session_id: str,
    final_report: Dict[str, Any],
    answers: List[Dict[str, Any]],
    db: AsyncSession | None = None,
    expected_socket_id: str | None = None,
    expected_generation: int | None = None,
    expected_claim_id: str | None = None,
) -> bool:
    """Mark a MockInterview row as completed and persist scores/transcript/evaluation."""
    from backend.infrastructure.database.database import AsyncSessionLocal
    from sqlalchemy import select, update

    async def _run(session):
        try:
            result = await session.execute(
                select(
                    MockInterview.id,
                    MockInterview.candidate_id,
                    MockInterview.status,
                    MockInterview.connection_state,
                    MockInterview.connection_generation,
                    MockInterview.claim_id,
                )
                .where(MockInterview.session_id == session_id)
            )
            interview = result.one_or_none()
            if interview is None:
                logger.warning(
                    "complete_mock_interview: no MockInterview found for session_id=%s",
                    session_id,
                )
                return False

            if interview.status != "in_progress":
                logger.info(
                    "complete_mock_interview: skipped row not in progress for session_id=%s",
                    session_id,
                )
                return False

            avg = _average_scores(answers)
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            transcript = _build_transcript(answers)

            try:
                evaluation = json.dumps(
                    {
                        "final_report": final_report,
                        "per_question": [
                            {
                                "question": answer.get("question"),
                                "skill": answer.get("skill"),
                                "scores": (answer.get("evaluation") or {}).get("scores"),
                                "summary": (answer.get("evaluation") or {}).get("summary"),
                            }
                            for answer in answers
                        ],
                    },
                    default=str,
                )
            except Exception:
                logger.warning("Could not serialize evaluation payload; skipping")
                evaluation = None

            # Recheck eligibility in the write itself. This prevents a stale
            # read or concurrent abandonment/completion from overwriting a
            # terminal status or repeating completion side effects.
            updated = await session.execute(
                update(MockInterview)
                .where(
                    MockInterview.id == interview.id,
                    MockInterview.status == "in_progress",
                    *(
                        [
                            MockInterview.connection_state == "active",
                            MockInterview.connection_generation == expected_generation,
                            MockInterview.claim_id == expected_claim_id,
                        ]
                        if expected_socket_id
                        else []
                    ),
                )
                .values(
                    status="completed",
                    connection_state="completed",
                    claim_lease_until=None,
                    completed_at=now,
                    score=avg["overall"],
                    technical_score=avg["technical"],
                    communication_score=avg["behavioral"],
                    reasoning_score=avg["reasoning"],
                    transcript=transcript,
                    evaluation=evaluation,
                )
            )
            if updated.rowcount != 1:
                await session.rollback()
                logger.info(
                    "complete_mock_interview: row no longer eligible for session_id=%s",
                    session_id,
                )
                return False

            # Decrement credits ONLY upon successful completion
            from backend.models.candidate_portal import CandidateProfile
            result_profile = await session.execute(
                select(CandidateProfile).filter(CandidateProfile.id == interview.candidate_id)
            )
            profile = result_profile.scalar_one_or_none()
            if profile:
                if profile.mock_interviews_remaining > 0:
                    profile.mock_interviews_remaining -= 1
                    logger.info(f"Deducted 1 credit from user_id={profile.user_id}. Remaining: {profile.mock_interviews_remaining}")
                else:
                    logger.warning(f"User {profile.user_id} completed interview but has 0 credits?")

            # Redis and SQL cannot share a transaction. Recheck ownership as
            # late as possible before committing so a superseded socket does
            # not knowingly finalize the record.
            if expected_socket_id:
                from backend.modules.interview.sessions.registry import get_session_registry

                if (
                    expected_generation is None
                    or expected_claim_id is None
                    or not await get_session_registry().owns_session(
                        session_id,
                        expected_socket_id,
                        generation=expected_generation,
                        claim_id=expected_claim_id,
                    )
                ):
                    await session.rollback()
                    logger.info(
                        "complete_mock_interview: socket ownership changed before commit",
                        extra={"extra_data": {"session_id": session_id}},
                    )
                    return False
            
            interview_id = interview.id
            await session.commit()

            logger.info(
                "MockInterview completed",
                extra={
                    "extra_data": {
                        "session_id": session_id,
                        "interview_id": interview_id,
                        "overall": avg["overall"],
                        "technical": avg["technical"],
                        "behavioral": avg["behavioral"],
                        "reasoning": avg["reasoning"],
                        "answers_count": len(answers),
                    }
                },
            )
            return True

        except Exception:
            logger.exception("Failed to persist MockInterview for session_id=%s", session_id)
            try:
                await session.rollback()
            except Exception:
                pass
            return False

    if db is not None:
        return await _run(db)
    async with AsyncSessionLocal() as session:
        return await _run(session)


async def fail_mock_interview(
    session_id: str,
    reason: str = "error",
    db: AsyncSession | None = None,
    expected_generation: int | None = None,
    expected_claim_id: str | None = None,
) -> bool:
    """
    Mark an in-progress MockInterview row as abandoned.
    """
    from backend.infrastructure.database.database import AsyncSessionLocal
    from sqlalchemy import select, update

    async def _run(session):
        try:
            result = await session.execute(
                select(MockInterview.id, MockInterview.status)
                .where(MockInterview.session_id == session_id)
            )
            interview = result.one_or_none()
            if not interview:
                return False

            # FIX: never downgrade a completed row
            if interview.status == "completed":
                logger.info(
                    "fail_mock_interview: skipped — row already completed",
                    extra={"extra_data": {"session_id": session_id, "reason": reason}},
                )
                return False

            if interview.status != "in_progress":
                return False

            conditions = [
                MockInterview.id == interview.id,
                MockInterview.status == "in_progress",
            ]
            if expected_generation is not None and expected_claim_id:
                conditions.extend([
                    MockInterview.connection_state == "active",
                    MockInterview.connection_generation == expected_generation,
                    MockInterview.claim_id == expected_claim_id,
                ])
            updated = await session.execute(
                update(MockInterview)
                .where(*conditions)
                .values(
                    status="abandoned",
                    connection_state="abandoned",
                    claim_lease_until=None,
                    completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
            if updated.rowcount != 1:
                await session.rollback()
                return False
            await session.commit()

            logger.info(
                "MockInterview marked abandoned",
                extra={"extra_data": {"session_id": session_id, "reason": reason}},
            )
            return True

        except Exception:
            logger.exception("Failed to mark MockInterview abandoned for session_id=%s", session_id)
            try:
                await session.rollback()
            except Exception:
                pass
            return False

    if db is not None:
        return await _run(db)
    async with AsyncSessionLocal() as session:
        return await _run(session)
