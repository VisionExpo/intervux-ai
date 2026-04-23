from __future__ import annotations

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator
from backend.core.llm_brain import run_safe_json_task, BaseEvaluationModel

EXTRACT_CONCEPTS_PROMPT_TEMPLATE = """
Extract technical concepts used in this answer.
Return JSON:
{{
  "concepts": ["..."]
}}
Answer: {answer}
""".strip()

VERIFY_CONCEPTS_PROMPT_TEMPLATE = """
Verify whether the concepts are used correctly in the answer.
Return JSON:
{{
  "concept_correctness": 0,
  "misused_terms": ["..."],
  "contradictions": ["..."],
  "hallucination_detected": false,
  "notes": ["..."]
}}
Question: {question}
Answer: {answer}
Concepts: {concepts}
Reasoning Steps: {reasoning_steps}
""".strip()


class ConceptsExtractionModel(BaseEvaluationModel):
    concepts: List[str] = Field(default_factory=list)

    @field_validator("concepts", mode="before")
    @classmethod
    def normalize_concepts(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


class ConsistencyVerificationModel(BaseEvaluationModel):
    concept_correctness: int = 0
    misused_terms: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    hallucination_detected: bool = False
    notes: List[str] = Field(default_factory=list)

    @field_validator("concept_correctness")
    @classmethod
    def clamp_score(cls, v: int) -> int:
        return max(0, min(10, v))

    @field_validator("misused_terms", "contradictions", "notes", mode="before")
    @classmethod
    def normalize_lists(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


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
        result = run_safe_json_task(
            prompt, ConceptsExtractionModel, temperature=0.1, fallback_factory=ConceptsExtractionModel
        )
        return result.concepts[:12]

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
        result = run_safe_json_task(
            prompt,
            ConsistencyVerificationModel,
            temperature=0.1,
            fallback_factory=ConsistencyVerificationModel,
        )

        concept_correctness = result.concept_correctness
        hallucination_detected = result.hallucination_detected
        llm_misused = result.misused_terms
        llm_contradictions = result.contradictions
        llm_notes = result.notes[:10]

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
