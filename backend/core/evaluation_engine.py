from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict

from pydantic import BaseModel, ValidationError

from backend.core.llm_brain import _run_json_task
from backend.core.consistency_checker import ConsistencyChecker
from backend.core.reasoning_analyzer import ReasoningAnalyzer
from backend.core.self_consistency import SelfConsistencyEvaluator
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics
from backend.utils.research_logger import research_logger

logger = get_logger(__name__)

TECH_WEIGHT = 0.7
BEHAVIOR_WEIGHT = 0.3

class EvaluationFatalError(Exception):
    """Raised when evaluation fails conclusively after all retries."""
    pass

class TechnicalEvalResult(BaseModel):
    accuracy: int
    depth: int
    problem_solving: int

class BehavioralEvalResult(BaseModel):
    clarity: int
    confidence: int
    structure: int

TECH_PROMPT_TEMPLATE = """
Evaluate the technical correctness of this answer.
{ideal_rubric}
Return JSON only:
{{
  "accuracy": 0,
  "depth": 0,
  "problem_solving": 0
}}
Question: {question}
Answer: <candidate_answer>{answer}</candidate_answer>
""".strip()

BEHAVIOR_PROMPT_TEMPLATE = """
Evaluate communication quality.
Return JSON only:
{{
  "clarity": 0,
  "confidence": 0,
  "structure": 0
}}
Answer: <candidate_answer>{answer}</candidate_answer>
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
        ideal_rubric = "Focus precisely on correct identification of technical principles taught in standard engineering pipelines. An ideal answer (10/10) directly names the key technology/concept without hesitation, details its fundamental structural operation, and highlights practical tradeoffs."
        prompt = TECH_PROMPT_TEMPLATE.format(question=question, answer=answer, ideal_rubric=ideal_rubric)
        
        for attempt in range(3):
            try:
                payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
                TechnicalEvalResult.model_validate(payload)
                return {
                    "accuracy": _clamp_score(payload.get("accuracy", 0)),
                    "depth": _clamp_score(payload.get("depth", 0)),
                    "problem_solving": _clamp_score(payload.get("problem_solving", 0)),
                }
            except ValidationError as e:
                logger.warning(f"Technical validation failed on attempt {attempt+1}: {str(e)}")
                prompt += f"\n[SYSTEM VERIFICATION ERROR] Your previous payload was invalid: {str(e)}. Emit ONLY raw valid JSON dict."
        
        raise EvaluationFatalError("LLM failed technical evaluation JSON schema matching after 3 retries.")

    def behavioral_eval(self, answer: str) -> Dict[str, int]:
        prompt = BEHAVIOR_PROMPT_TEMPLATE.format(answer=answer)
        for attempt in range(3):
            try:
                payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
                BehavioralEvalResult.model_validate(payload)
                return {
                    "clarity": _clamp_score(payload.get("clarity", 0)),
                    "confidence": _clamp_score(payload.get("confidence", 0)),
                    "structure": _clamp_score(payload.get("structure", 0)),
                }
            except ValidationError as e:
                logger.warning(f"Behavioral validation failed on attempt {attempt+1}: {str(e)}")
                prompt += f"\n[SYSTEM VERIFICATION ERROR] Your previous payload was invalid: {str(e)}. Emit ONLY raw valid JSON dict."
        
        raise EvaluationFatalError("LLM failed behavioral evaluation JSON schema matching after 3 retries.")

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
        def _run_coro(coro: Any) -> Any:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                return asyncio.run(coro)
            with ThreadPoolExecutor(max_workers=1) as executor:
                return executor.submit(lambda: asyncio.run(coro)).result()

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

        def _evaluate_concurrent(
            q: str, a: str, p: Dict[str, Any] | None
        ) -> Dict[str, Any]:
            with ThreadPoolExecutor(max_workers=3) as executor:
                base_future = executor.submit(
                    _dual_eval_engine.evaluate, question=q, answer=a, profile=p
                )
                reasoning_future = executor.submit(
                    _reasoning_analyzer.analyze, question=q, answer=a
                )
                
                # If these raise Exception or EvaluationFatalError, it will bubble out here
                base_eval = base_future.result()
                reasoning = reasoning_future.result()

            consistency = _consistency_checker.check(
                    question=q,
                    answer=a,
                    reasoning_steps=reasoning.get("steps", []),
                )
            base_eval["reasoning"] = reasoning
            base_eval["consistency"] = consistency
            adjustment_factor = float(
                consistency.get("technical_adjustment_factor", 1.0)
            )
            if adjustment_factor < 1.0:
                for key in ("accuracy", "depth", "problem_solving"):
                    base_eval["technical"][key] = _clamp_score(
                        round(float(base_eval["technical"].get(key, 0)) * adjustment_factor)
                    )
                base_eval["final"] = _dual_eval_engine.fuse_scores(
                    base_eval["technical"], base_eval["behavioral"]
                )
            return base_eval

        combined = _evaluate_concurrent(question, answer, profile)
        reasoning = combined.get("reasoning", {})
        consistency = combined.get("consistency", {})
        tech = combined["technical"]
        behavior = combined["behavioral"]
        final_score = float(combined["final"])
        tech_avg = _avg(tech)
        beh_avg = _avg(behavior)
        
        # New robust composite confidence replacing pure LLM text variation
        initial_confidence = round(
            max(0.0, min(1.0, 1.0 - abs(tech_avg - beh_avg) / 10.0)), 2
        )

        if initial_confidence >= SELF_CONSISTENCY_THRESHOLD or _self_consistency.passes <= 1:
            result = _format_dual_payload(
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
            research_logger.write_evaluation_record({
                "question": question,
                "answer": answer,
                "score": result.get("final", {}).get("score", 0),
                "reasoning_score": result.get("reasoning", {}).get("reasoning_score", 0),
                "concept_consistency_score": result.get("consistency", {}).get("concept_consistency_score", 0),
                "hallucination_risk": result.get("consistency", {}).get("hallucination_risk", 0),
                "provider": result.get("meta", {}).get("provider", "unknown"),
                "skill": (profile or {}).get("skills", ["unknown"])[0] if profile else "unknown",
            })
            metrics.record_latency("dual_eval_final_score", final_score)
            return result

        if SELF_CONSISTENCY_PARALLEL:
            aggregate = _run_coro(
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
        result = _format_dual_payload(
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
        research_logger.write_evaluation_record({
            "question": question,
            "answer": answer,
            "score": result.get("final", {}).get("score", 0),
            "reasoning_score": result.get("reasoning", {}).get("reasoning_score", 0),
            "concept_consistency_score": result.get("consistency", {}).get("concept_consistency_score", 0),
            "hallucination_risk": result.get("consistency", {}).get("hallucination_risk", 0),
            "provider": result.get("meta", {}).get("provider", "unknown"),
            "skill": (profile or {}).get("skills", ["unknown"])[0] if profile else "unknown",
        })
        return result
        
    except EvaluationFatalError:
        metrics.record_error()
        logger.exception("Dual evaluation fatal error encountered. Re-raising to router context.")
        raise
    except Exception as e:
        metrics.record_error()
        logger.exception(f"Unexpected Evaluation Crash: {e}. Coercing to FatalError to trigger retry.")
        raise EvaluationFatalError(f"Unexpected Eval crash: {str(e)}")
