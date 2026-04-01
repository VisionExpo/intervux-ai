"""
Interview Persistence Service
==============================

Writes live interview results back to the MockInterview table so that
candidates can see their scores in the history page after a session ends.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List

from backend.db.database import SessionLocal
from backend.models.candidate_portal import MockInterview
from backend.utils.logger import get_logger

logger = get_logger(__name__)


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
) -> bool:
    """Mark a MockInterview row as completed and persist scores/transcript/evaluation."""
    from backend.db.database import AsyncSessionLocal
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(MockInterview).filter(MockInterview.session_id == session_id))
            interview = result.scalar_one_or_none()
            if not interview:
                logger.warning(
                    "complete_mock_interview: no MockInterview found for session_id=%s",
                    session_id,
                )
                return False

            avg = _average_scores(answers)

            interview.status = "completed"
            interview.completed_at = datetime.utcnow()
            interview.score = avg["overall"]
            interview.technical_score = avg["technical"]
            interview.communication_score = avg["behavioral"]
            interview.reasoning_score = avg["reasoning"]
            interview.transcript = _build_transcript(answers)

            try:
                interview.evaluation = json.dumps(
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

            await db.commit()

            logger.info(
                "MockInterview completed",
                extra={
                    "extra_data": {
                        "session_id": session_id,
                        "interview_id": interview.id,
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
                await db.rollback()
            except Exception:
                pass
            return False


async def fail_mock_interview(session_id: str, reason: str = "error") -> bool:
    """
    Mark an in-progress MockInterview row as abandoned.

    FIX: Guard added — if the row is already 'completed' (set by
    complete_mock_interview just before cleanup() runs), do not overwrite it.
    Without this guard a race between complete_mock_interview and the
    finally-block cleanup() call would reset a completed row to 'abandoned'.
    """
    from backend.db.database import AsyncSessionLocal
    from sqlalchemy import select
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(MockInterview).filter(MockInterview.session_id == session_id))
            interview = result.scalar_one_or_none()
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

            interview.status = "abandoned"
            interview.completed_at = datetime.utcnow()
            await db.commit()

            logger.info(
                "MockInterview marked abandoned",
                extra={"extra_data": {"session_id": session_id, "reason": reason}},
            )
            return True

        except Exception:
            logger.exception("Failed to mark MockInterview abandoned for session_id=%s", session_id)
            try:
                await db.rollback()
            except Exception:
                pass
            return False
