from __future__ import annotations

import re
from typing import Any, Dict, List

from backend.core.llm_brain import _run_json_task

EXTRACT_CONCEPTS_PROMPT_TEMPLATE = """
Extract technical concepts used in this answer.
Return JSON:
{
  "concepts": ["..."]
}
Answer: {answer}
""".strip()

VERIFY_CONCEPTS_PROMPT_TEMPLATE = """
Verify whether the concepts are used correctly in the answer.
Return JSON:
{
  "concept_correctness": 0,
  "misused_terms": ["..."],
  "contradictions": ["..."],
  "hallucination_detected": false,
  "notes": ["..."]
}
Question: {question}
Answer: {answer}
Concepts: {concepts}
Reasoning Steps: {reasoning_steps}
""".strip()


def _clamp_score(value: Any) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = 0
    return max(0, min(10, parsed))


def _normalize_str_list(value: Any, limit: int = 8) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out[:limit]


class ConsistencyChecker:
    def _heuristic_term_misuse(self, answer: str) -> List[str]:
        text = answer.lower()
        flags: List[str] = []
        if "dropout" in text and "inference" in text and "apply" in text:
            flags.append("dropout_usage_claim_needs_verification")
        if "gradient descent" in text and "always converges" in text:
            flags.append("absolute_convergence_claim")
        if "transformer" in text and "no attention" in text:
            flags.append("transformer_attention_contradiction")
        return flags

    def _heuristic_contradictions(self, answer: str) -> List[str]:
        text = answer.lower()
        contradictions: List[str] = []
        # lightweight contradiction checks
        if re.search(r"\b(always|never)\b", text) and "depends" in text:
            contradictions.append("contains absolute and conditional claims")
        if "no overfitting" in text and "regularization needed" in text:
            contradictions.append("overfitting denial vs regularization need")
        return contradictions

    def extract_concepts(self, answer: str) -> List[str]:
        prompt = EXTRACT_CONCEPTS_PROMPT_TEMPLATE.format(answer=answer)
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
        return _normalize_str_list(payload.get("concepts", []), limit=12)

    def verify_concepts(
        self,
        question: str,
        answer: str,
        concepts: List[str],
        reasoning_steps: List[str] | None = None,
    ) -> Dict[str, Any]:
        prompt = VERIFY_CONCEPTS_PROMPT_TEMPLATE.format(
            question=question,
            answer=answer,
            concepts=concepts or [],
            reasoning_steps=reasoning_steps or [],
        )
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)

        concept_correctness = _clamp_score(payload.get("concept_correctness", 0))
        hallucination_detected = bool(payload.get("hallucination_detected", False))
        llm_misused = _normalize_str_list(payload.get("misused_terms", []))
        llm_contradictions = _normalize_str_list(payload.get("contradictions", []))
        llm_notes = _normalize_str_list(payload.get("notes", []), limit=10)

        heuristic_misused = self._heuristic_term_misuse(answer)
        heuristic_contradictions = self._heuristic_contradictions(answer)

        misused_terms = sorted(set(llm_misused + heuristic_misused))
        contradictions = sorted(set(llm_contradictions + heuristic_contradictions))
        if hallucination_detected:
            contradictions = sorted(set(contradictions + ["possible_hallucinated_explanation"]))

        hallucination_risk = 8 if hallucination_detected else 2
        if contradictions:
            hallucination_risk = max(hallucination_risk, 5)
        if misused_terms:
            hallucination_risk = max(hallucination_risk, 4)
        concept_consistency_score = concept_correctness
        consistency_score = concept_correctness
        technical_adjustment_factor = 0.7 if consistency_score < 5 else 1.0

        return {
            "concepts": concepts,
            "concept_correctness": concept_correctness,
            "hallucination_risk": hallucination_risk,
            "hallucination_detected": hallucination_detected,
            "misused_terms": misused_terms,
            "contradictions": contradictions,
            "concept_consistency_score": concept_consistency_score,
            "consistency_score": consistency_score,
            "technical_adjustment_factor": technical_adjustment_factor,
            "consistency_penalty": round(10.0 - consistency_score, 2),
            "notes": llm_notes,
        }

    @staticmethod
    def consistency_score(metrics: Dict[str, Any]) -> float:
        return float(metrics.get("concept_correctness", 0))

    def check(
        self, question: str, answer: str, reasoning_steps: List[str] | None = None
    ) -> Dict[str, Any]:
        concepts = self.extract_concepts(answer)
        consistency = self.verify_concepts(
            question=question,
            answer=answer,
            concepts=concepts,
            reasoning_steps=reasoning_steps,
        )
        return consistency

    # Backward-compatible alias used by existing pipeline.
    def evaluate(
        self, question: str, answer: str, reasoning_steps: List[str] | None = None
    ) -> Dict[str, Any]:
        return self.check(question=question, answer=answer, reasoning_steps=reasoning_steps)
