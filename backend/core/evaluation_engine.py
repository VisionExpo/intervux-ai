from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from backend.core.llm_brain import _run_json_task
from backend.core.self_consistency import SelfConsistencyEvaluator
from backend.utils.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)

TECH_WEIGHT = 0.7
BEHAVIOR_WEIGHT = 0.3

TECH_PROMPT_TEMPLATE = """
Evaluate the technical correctness of this answer.
Return JSON only:
{
  "accuracy": 0,
  "depth": 0,
  "problem_solving": 0
}
Question: {question}
Answer: {answer}
""".strip()

BEHAVIOR_PROMPT_TEMPLATE = """
Evaluate communication quality.
Return JSON only:
{
  "clarity": 0,
  "confidence": 0,
  "structure": 0
}
Answer: {answer}
""".strip()


def _clamp_score(value: Any) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = 0
    return max(0, min(10, parsed))


def _avg(values: Dict[str, int]) -> float:
    if not values:
        return 0.0
    return sum(values.values()) / float(len(values))


class DualEvaluationEngine:
    def technical_eval(self, question: str, answer: str, _profile: Dict[str, Any] | None = None) -> Dict[str, int]:
        prompt = TECH_PROMPT_TEMPLATE.format(question=question, answer=answer)
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
        return {
            "accuracy": _clamp_score(payload.get("accuracy", 0)),
            "depth": _clamp_score(payload.get("depth", 0)),
            "problem_solving": _clamp_score(payload.get("problem_solving", 0)),
        }

    def behavioral_eval(self, answer: str) -> Dict[str, int]:
        prompt = BEHAVIOR_PROMPT_TEMPLATE.format(answer=answer)
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
        return {
            "clarity": _clamp_score(payload.get("clarity", 0)),
            "confidence": _clamp_score(payload.get("confidence", 0)),
            "structure": _clamp_score(payload.get("structure", 0)),
        }

    def fuse_scores(self, tech: Dict[str, int], behavior: Dict[str, int]) -> float:
        tech_score = _avg(tech)
        beh_score = _avg(behavior)
        final = (tech_score * TECH_WEIGHT) + (beh_score * BEHAVIOR_WEIGHT)
        return round(final, 2)

    def evaluate(self, question: str, answer: str, profile: Dict[str, Any] | None = None) -> Dict[str, Any]:
        tech = self.technical_eval(question, answer, profile)
        behavior = self.behavioral_eval(answer)
        final = self.fuse_scores(tech, behavior)
        return {
            "technical": tech,
            "behavioral": behavior,
            "final": final,
        }


_dual_eval_engine = DualEvaluationEngine()
_self_consistency = SelfConsistencyEvaluator(
    passes=int(os.getenv("SELF_CONSISTENCY_PASSES", "3"))
)
SELF_CONSISTENCY_THRESHOLD = float(os.getenv("SELF_CONSISTENCY_THRESHOLD", "0.8"))
SELF_CONSISTENCY_PARALLEL = os.getenv("SELF_CONSISTENCY_PARALLEL", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


def _format_dual_payload(
    tech: Dict[str, int],
    behavior: Dict[str, int],
    final_score: float,
    confidence: float,
    variance: float,
    pass_count: int,
    spread: float,
) -> Dict[str, Any]:
    tech_avg = _avg(tech)
    beh_avg = _avg(behavior)
    return {
        "technical": tech,
        "behavioral": behavior,
        "final": {"score": round(float(final_score), 2)},
        "scores": {
            "Technical": round(tech_avg, 2),
            "Behavioral": round(beh_avg, 2),
            "Overall": round(float(final_score), 2),
        },
        "feedback": [
            f"Technical average: {round(tech_avg, 2)}",
            f"Behavioral average: {round(beh_avg, 2)}",
        ],
        "summary": (
            f"Technical Score: {round(tech_avg, 2)}, "
            f"Behavioral Score: {round(beh_avg, 2)}, "
            f"Final Score: {round(float(final_score), 2)}"
        ),
        "confidence_score": round(float(confidence), 2),
        "evaluator_variance": round(float(variance), 3),
        "meta": {
            "provider": "dual_evaluation",
            "tech_weight": TECH_WEIGHT,
            "behavior_weight": BEHAVIOR_WEIGHT,
            "self_consistency_passes": pass_count,
            "self_consistency_spread": round(float(spread), 3),
        },
    }


def evaluate_answer_dual(question: str, answer: str, profile: Dict[str, Any] | None = None, **_kwargs: Any) -> Dict[str, Any]:
    try:
        combined = _dual_eval_engine.evaluate(question=question, answer=answer, profile=profile)
        tech = combined["technical"]
        behavior = combined["behavioral"]
        final_score = float(combined["final"])
        tech_avg = _avg(tech)
        beh_avg = _avg(behavior)
        initial_confidence = round(
            max(0.0, min(1.0, 1.0 - abs(tech_avg - beh_avg) / 10.0)), 2
        )

        if initial_confidence >= SELF_CONSISTENCY_THRESHOLD or _self_consistency.passes <= 1:
            metrics.record_latency("dual_eval_final_score", final_score)
            return _format_dual_payload(
                tech=tech,
                behavior=behavior,
                final_score=final_score,
                confidence=initial_confidence,
                variance=abs(tech_avg - beh_avg),
                pass_count=1,
                spread=0.0,
            )

        if SELF_CONSISTENCY_PARALLEL:
            aggregate = asyncio.run(
                _self_consistency.evaluate_parallel(
                    _dual_eval_engine.evaluate, question, answer, profile
                )
            )
        else:
            aggregate = _self_consistency.evaluate(
                _dual_eval_engine.evaluate, question, answer, profile
            )

        metrics.record_latency("dual_eval_final_score", aggregate.get("final_score", final_score))
        metrics.record_latency(
            "evaluation_variance", float(aggregate.get("spread", 0.0))
        )
        return _format_dual_payload(
            tech=aggregate.get("technical", tech),
            behavior=aggregate.get("behavioral", behavior),
            final_score=float(aggregate.get("final_score", final_score)),
            confidence=float(aggregate.get("confidence", initial_confidence)),
            variance=float(aggregate.get("spread", abs(tech_avg - beh_avg))),
            pass_count=int(aggregate.get("pass_count", _self_consistency.passes)),
            spread=float(aggregate.get("spread", 0.0)),
        )
    except Exception:
        metrics.record_error()
        logger.exception("Dual evaluation failed")
        return {
            "technical": {"accuracy": 5, "depth": 5, "problem_solving": 5},
            "behavioral": {"clarity": 5, "confidence": 5, "structure": 5},
            "final": {"score": 5.0},
            "scores": {"Technical": 5.0, "Behavioral": 5.0, "Overall": 5.0},
            "feedback": ["Evaluation fallback triggered."],
            "summary": "Dual evaluation failed.",
            "confidence_score": 0.2,
            "evaluator_variance": 3.0,
            "meta": {
                "provider": "dual_evaluation_fallback",
                "tech_weight": TECH_WEIGHT,
                "behavior_weight": BEHAVIOR_WEIGHT,
            },
        }
