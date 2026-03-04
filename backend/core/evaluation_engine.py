from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from backend.core.llm_brain import _run_json_task
from backend.core.consistency_checker import ConsistencyChecker
from backend.core.reasoning_analyzer import ReasoningAnalyzer
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
_reasoning_analyzer = ReasoningAnalyzer()
_consistency_checker = ConsistencyChecker()
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
    reasoning: Dict[str, Any] | None = None,
    consistency: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    tech_avg = _avg(tech)
    beh_avg = _avg(behavior)
    reasoning_payload = reasoning or {
        "steps": [],
        "logic_flow": "unclear",
        "metrics": {
            "logical_consistency": 0,
            "step_completeness": 0,
            "causal_reasoning": 0,
        },
        "reasoning_score": 0.0,
    }
    reasoning_score = float(reasoning_payload.get("reasoning_score", 0.0))
    consistency_payload = consistency or {
        "concepts": [],
        "concept_correctness": 0,
        "hallucination_risk": 0,
        "hallucination_detected": False,
        "misused_terms": [],
        "contradictions": [],
        "concept_consistency_score": 0,
        "consistency_score": 0,
        "technical_adjustment_factor": 1.0,
        "consistency_penalty": 0.0,
        "notes": [],
    }

    feedback = [
        f"Technical average: {round(tech_avg, 2)}",
        f"Behavioral average: {round(beh_avg, 2)}",
    ]
    if reasoning_payload.get("shallow_or_memorized"):
        feedback.append("Reasoning appears shallow or potentially memorized.")

    if consistency_payload.get("misused_terms"):
        feedback.append("Detected potentially misused technical terms.")
    if consistency_payload.get("contradictions"):
        feedback.append("Detected possible contradictions in explanation.")

    return {
        "technical": tech,
        "behavioral": behavior,
        "reasoning": reasoning_payload,
        "consistency": consistency_payload,
        "final": {"score": round(float(final_score), 2)},
        "scores": {
            "Technical": round(tech_avg, 2),
            "Behavioral": round(beh_avg, 2),
            "Reasoning": round(reasoning_score, 2),
            "ConceptConsistency": round(
                float(consistency_payload.get("concept_consistency_score", 0)), 2
            ),
            "Consistency": round(
                float(consistency_payload.get("consistency_score", 0)), 2
            ),
            "Overall": round(float(final_score), 2),
        },
        "feedback": feedback,
        "summary": (
            f"Technical Score: {round(tech_avg, 2)}, "
            f"Behavioral Score: {round(beh_avg, 2)}, "
            f"Reasoning Score: {round(reasoning_score, 2)}, "
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
            "reasoning_signals": reasoning_payload.get("signals", []),
            "shallow_or_memorized": bool(
                reasoning_payload.get("shallow_or_memorized", False)
            ),
            "hallucination_risk": consistency_payload.get("hallucination_risk", 0),
            "hallucination_detected": bool(
                consistency_payload.get("hallucination_detected", False)
            ),
            "misused_terms": consistency_payload.get("misused_terms", []),
            "contradictions": consistency_payload.get("contradictions", []),
        },
    }


def evaluate_answer_dual(question: str, answer: str, profile: Dict[str, Any] | None = None, **_kwargs: Any) -> Dict[str, Any]:
    try:
        def _evaluate_with_reasoning(
            q: str, a: str, p: Dict[str, Any] | None
        ) -> Dict[str, Any]:
            base = _dual_eval_engine.evaluate(question=q, answer=a, profile=p)
            base["reasoning"] = _reasoning_analyzer.analyze(question=q, answer=a)
            base["consistency"] = _consistency_checker.check(
                question=q,
                answer=a,
                reasoning_steps=base["reasoning"].get("steps", []),
            )
            adjustment_factor = float(
                base["consistency"].get("technical_adjustment_factor", 1.0)
            )
            if adjustment_factor < 1.0:
                for key in ("accuracy", "depth", "problem_solving"):
                    base["technical"][key] = _clamp_score(
                        round(float(base["technical"].get(key, 0)) * adjustment_factor)
                    )
                base["final"] = _dual_eval_engine.fuse_scores(
                    base["technical"], base["behavioral"]
                )
            return base

        combined = _evaluate_with_reasoning(question, answer, profile)
        reasoning = combined.get("reasoning", {})
        consistency = combined.get("consistency", {})
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
                reasoning=reasoning,
                consistency=consistency,
            )

        if SELF_CONSISTENCY_PARALLEL:
            aggregate = asyncio.run(
                _self_consistency.evaluate_parallel(
                    _evaluate_with_reasoning, question, answer, profile
                )
            )
        else:
            aggregate = _self_consistency.evaluate(
                _evaluate_with_reasoning, question, answer, profile
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
            reasoning={
                "steps": aggregate.get("reasoning_steps", reasoning.get("steps", [])),
                "logic_flow": aggregate.get("logic_flow", reasoning.get("logic_flow", "unclear")),
                "metrics": aggregate.get(
                    "reasoning_metrics", reasoning.get("metrics", {})
                ),
                "reasoning_score": float(
                    aggregate.get("reasoning_score", reasoning.get("reasoning_score", 0.0))
                ),
            },
            consistency={
                "hallucination_risk": aggregate.get(
                    "hallucination_risk", consistency.get("hallucination_risk", 0)
                ),
                "hallucination_detected": bool(
                    aggregate.get(
                        "hallucination_risk", consistency.get("hallucination_risk", 0)
                    )
                    >= 6
                ),
                "misused_terms": aggregate.get(
                    "misused_terms", consistency.get("misused_terms", [])
                ),
                "contradictions": aggregate.get(
                    "contradictions", consistency.get("contradictions", [])
                ),
                "concepts": consistency.get("concepts", []),
                "concept_correctness": aggregate.get(
                    "concept_consistency_score",
                    consistency.get("concept_correctness", 0),
                ),
                "concept_consistency_score": aggregate.get(
                    "concept_consistency_score",
                    consistency.get("concept_consistency_score", 0),
                ),
                "consistency_score": aggregate.get(
                    "concept_consistency_score", consistency.get("consistency_score", 0)
                ),
                "technical_adjustment_factor": consistency.get(
                    "technical_adjustment_factor", 1.0
                ),
                "consistency_penalty": aggregate.get(
                    "consistency_penalty", consistency.get("consistency_penalty", 0.0)
                ),
                "notes": aggregate.get("consistency_notes", consistency.get("notes", [])),
            },
        )
    except Exception:
        metrics.record_error()
        logger.exception("Dual evaluation failed")
        return {
            "technical": {"accuracy": 5, "depth": 5, "problem_solving": 5},
            "behavioral": {"clarity": 5, "confidence": 5, "structure": 5},
            "reasoning": {
                "steps": [],
                "logic_flow": "unclear",
                "metrics": {
                    "logical_consistency": 5,
                    "step_completeness": 5,
                    "causal_reasoning": 5,
                },
                "reasoning_score": 5.0,
            },
            "consistency": {
                "concepts": [],
                "concept_correctness": 5,
                "hallucination_risk": 5,
                "hallucination_detected": False,
                "misused_terms": [],
                "contradictions": [],
                "concept_consistency_score": 5,
                "consistency_score": 5,
                "technical_adjustment_factor": 1.0,
                "consistency_penalty": 0.0,
                "notes": [],
            },
            "final": {"score": 5.0},
            "scores": {
                "Technical": 5.0,
                "Behavioral": 5.0,
                "Reasoning": 5.0,
                "ConceptConsistency": 5.0,
                "Consistency": 5.0,
                "Overall": 5.0,
            },
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
