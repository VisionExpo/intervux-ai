from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator
from backend.core.llm_brain import run_safe_json_task, BaseEvaluationModel

EXTRACT_REASONING_TEMPLATE = """
Extract reasoning steps from the answer.
Return JSON:
{{
  "steps": ["..."],
  "logic_flow": "clear"
}}
Answer: {answer}
""".strip()

EVALUATE_REASONING_TEMPLATE = """
Evaluate reasoning quality.
Return JSON:
{{
  "logical_consistency": 0,
  "step_completeness": 0,
  "causal_reasoning": 0
}}
Question: {question}
Reasoning Steps: {steps_json}
Logic Flow: {logic_flow}
""".strip()


class ReasoningExtractionModel(BaseEvaluationModel):
    steps: List[str] = Field(default_factory=list)
    logic_flow: str = "unclear"

    @field_validator("steps", mode="before")
    @classmethod
    def normalize_steps(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            # Split by common delimiters if LLM returns a string
            return [s.strip() for s in re.split(r"[\n,;]", v) if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


class ReasoningEvaluationModel(BaseEvaluationModel):
    logical_consistency: int = 0
    step_completeness: int = 0
    causal_reasoning: int = 0
    confidence: float = 0.5

    @field_validator("logical_consistency", "step_completeness", "causal_reasoning")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        return max(0, min(10, v))

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class ReasoningAnalyzer:
    def extract_reasoning(self, answer: str) -> Dict[str, Any]:
        prompt = EXTRACT_REASONING_TEMPLATE.format(answer=answer)
        result = run_safe_json_task(
            prompt, ReasoningExtractionModel, temperature=0.1, fallback_factory=ReasoningExtractionModel
        )
        return {"steps": result.steps[:8], "logic_flow": result.logic_flow}

    def evaluate_reasoning(self, question: str, reasoning: Dict[str, Any]) -> Dict[str, float]:
        prompt = EVALUATE_REASONING_TEMPLATE.format(
            question=question,
            steps_json=reasoning.get("steps", []),
            logic_flow=reasoning.get("logic_flow", "unclear"),
        )
        result = run_safe_json_task(
            prompt, ReasoningEvaluationModel, temperature=0.1, fallback_factory=ReasoningEvaluationModel
        )
        return {
            "logical_consistency": float(result.logical_consistency),
            "step_completeness": float(result.step_completeness),
            "causal_reasoning": float(result.causal_reasoning),
            "confidence": result.confidence,
        }

    @staticmethod
    def compute_reasoning_score(metrics: Dict[str, float]) -> float:
        if not metrics:
            return 0.0
        # Exclude confidence from the average score
        scores = [v for k, v in metrics.items() if k != "confidence"]
        if not scores:
            return 0.0
        return round(sum(scores) / float(len(scores)), 2)

    @staticmethod
    def _detect_shallow_or_memorized(answer: str, steps: List[str], metrics: Dict[str, float]) -> Dict[str, Any]:
        text = answer.strip()
        words = re.findall(r"[A-Za-z0-9_+\-]+", text)
        word_count = len(words)
        unique_ratio = (len(set(w.lower() for w in words)) / float(word_count)) if word_count else 0.0

        causal_score = int(metrics.get("causal_reasoning", 0))
        completeness = int(metrics.get("step_completeness", 0))
        logic_consistency = int(metrics.get("logical_consistency", 0))

        short_answer = word_count < 14
        low_variety = word_count >= 8 and unique_ratio < 0.55
        few_steps = len(steps) <= 1
        low_reasoning = causal_score <= 3 and completeness <= 3
        weak_structure = logic_consistency <= 3 and len(steps) <= 2

        shallow_detected = short_answer or low_variety or few_steps or low_reasoning or weak_structure
        penalty = 0.0
        reasons: List[str] = []

        if short_answer:
            penalty += 1.2
            reasons.append("very_short_answer")
        if low_variety:
            penalty += 0.8
            reasons.append("low_lexical_variety")
        if few_steps:
            penalty += 0.8
            reasons.append("insufficient_reasoning_steps")
        if low_reasoning:
            penalty += 1.5
            reasons.append("low_causal_reasoning")
        if weak_structure:
            penalty += 0.7
            reasons.append("weak_logical_structure")

        return {
            "shallow_or_memorized": shallow_detected,
            "signals": reasons,
            "penalty": round(min(2.5, penalty), 2),
            "word_count": word_count,
            "unique_ratio": round(unique_ratio, 3),
        }

    def analyze(self, question: str, answer: str) -> Dict[str, Any]:
        reasoning = self.extract_reasoning(answer)
        metrics = self.evaluate_reasoning(question, reasoning)
        base_score = self.compute_reasoning_score(metrics)
        shallow = self._detect_shallow_or_memorized(
            answer=answer, steps=reasoning.get("steps", []), metrics=metrics
        )
        reasoning_score = round(max(0.0, base_score - float(shallow["penalty"])), 2)
        return {
            "steps": reasoning.get("steps", []),
            "logic_flow": reasoning.get("logic_flow", "unclear"),
            "metrics": metrics,
            "signals": shallow["signals"],
            "shallow_or_memorized": shallow["shallow_or_memorized"],
            "word_count": shallow["word_count"],
            "reasoning_score": reasoning_score,
        }
