import json
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator
from backend.core.llm_brain import run_safe_json_task, BaseEvaluationModel
from backend.core.logging.logger import get_logger
from backend.utils.metrics import metrics

logger = get_logger(__name__)

RUBRIC = [
    "Technical Accuracy",
    "Clarity",
    "Depth",
    "Communication",
]

PASS1_TEMPLATE = """
You are an expert technical interviewer.
Score the candidate answer from 0-10 for:
Technical Accuracy
Clarity
Depth
Communication
Return JSON only:
{{
  "scores": {{"Technical Accuracy": 0, "Clarity": 0, "Depth": 0, "Communication": 0}},
  "feedback": ["..."],
  "summary": "..."
}}
Question: {question}
Candidate Answer: {answer}
""".strip()

CRITIQUE_TEMPLATE = """
You are reviewing an interview evaluation.
Candidate Answer:
{answer}
Original Evaluation:
{evaluation_json}
Identify possible issues with the evaluation.
Check:
- Did the evaluator miss important points?
- Was the score too high or too low?
- Was the reasoning weak?
Return JSON:
{{
  "issues": ["..."],
  "suggested_score_adjustment": 0
}}
""".strip()


class Pass1EvaluationModel(BaseEvaluationModel):
    scores: Dict[str, int] = Field(default_factory=dict)
    feedback: List[str] = Field(default_factory=list)
    summary: str = ""

    @field_validator("scores")
    @classmethod
    def validate_rubric_keys(cls, v: Dict[str, Any]) -> Dict[str, int]:
        required = set(RUBRIC)
        normalized = {}
        for key in required:
            val = v.get(key, 0)
            try:
                num = int(val)
            except (ValueError, TypeError):
                num = 0
            normalized[key] = max(0, min(10, num))
        return normalized

    @field_validator("feedback", mode="before")
    @classmethod
    def normalize_feedback(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split("\n") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


class CritiquePassModel(BaseEvaluationModel):
    issues: List[str] = Field(default_factory=list)
    suggested_score_adjustment: int = 0

    @field_validator("suggested_score_adjustment")
    @classmethod
    def clamp_adjustment(cls, v: int) -> int:
        return max(-2, min(2, v))

    @field_validator("issues", mode="before")
    @classmethod
    def normalize_issues(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split("\n") if s.strip()]
        if not isinstance(v, list):
            return []
        return [str(s).strip() for s in v if s]


def evaluate_pass1(
    question: str,
    answer: str,
    _profile: Dict[str, Any] | None = None,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    prompt = PASS1_TEMPLATE.format(question=question, answer=answer)
    result = run_safe_json_task(
        prompt, Pass1EvaluationModel, temperature=temperature, fallback_factory=Pass1EvaluationModel
    )
    return {
        "scores": result.scores,
        "feedback": result.feedback,
        "summary": result.summary,
        "provider": "unknown",  # run_safe_json_task doesn't return provider yet
    }


def critique_pass(
    answer: str,
    evaluation: Dict[str, Any],
    temperature: float = 0.1,
) -> Dict[str, Any]:
    prompt = CRITIQUE_TEMPLATE.format(
        answer=answer,
        evaluation_json=json.dumps(evaluation, separators=(",", ":")),
    )
    result = run_safe_json_task(
        prompt, CritiquePassModel, temperature=temperature, fallback_factory=CritiquePassModel
    )
    return {
        "issues": result.issues,
        "suggested_score_adjustment": result.suggested_score_adjustment,
        "provider": "unknown",
    }


def adjust_scores(pass1_scores: Dict[str, int], adjustment: int) -> Dict[str, int]:
    final_scores: Dict[str, int] = {}
    for key in RUBRIC:
        base = int(pass1_scores.get(key, 0))
        final_scores[key] = max(0, min(10, base + adjustment))
    return final_scores


def compute_confidence(adjustment: int) -> float:
    confidence = 1.0 - (abs(adjustment) / 3.0)
    return round(max(0.0, min(1.0, confidence)), 2)


def evaluate_answer_multipass(
    question: str,
    answer: str,
    profile: Dict[str, Any] | None = None,
    **_kwargs: Any,
) -> Dict[str, Any]:
    try:
        pass1 = evaluate_pass1(question=question, answer=answer, _profile=profile)
        critique = critique_pass(answer=answer, evaluation=pass1)
        adjustment = critique["suggested_score_adjustment"]
        final_scores = adjust_scores(pass1["scores"], adjustment)
        confidence = compute_confidence(adjustment)

        metrics.record_latency("evaluation_pass1_adjustment", float(adjustment))
        return {
            "scores": final_scores,
            "feedback": pass1["feedback"],
            "summary": pass1["summary"],
            "confidence_score": confidence,
            "evaluator_variance": round(abs(adjustment), 3),
            "meta": {
                "provider": "multipass",
                "pass1_provider": pass1.get("provider"),
                "critique_provider": critique.get("provider"),
                "issues": critique.get("issues", []),
                "suggested_score_adjustment": adjustment,
            },
        }
    except Exception:
        metrics.record_error()
        logger.exception("Multipass evaluation failed")
        fallback = {name: 5 for name in RUBRIC}
        return {
            "scores": fallback,
            "feedback": ["Evaluation fallback triggered."],
            "summary": "AI multipass evaluation failed.",
            "confidence_score": 0.2,
            "evaluator_variance": 3.0,
            "meta": {
                "provider": "multipass_fallback",
                "issues": [],
                "suggested_score_adjustment": 0,
            },
        }
