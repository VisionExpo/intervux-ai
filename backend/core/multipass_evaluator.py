import json
from typing import Any, Dict, List

from backend.core.llm_brain import _run_json_task
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
{
  "scores": {"Technical Accuracy": 0, "Clarity": 0, "Depth": 0, "Communication": 0},
  "feedback": ["..."],
  "summary": "..."
}
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
{
  "issues": ["..."],
  "suggested_score_adjustment": 0
}
""".strip()


def _clamp_score(value: Any) -> int:
    try:
        number = int(value)
    except Exception:
        number = 0
    return max(0, min(10, number))


def _normalize_scores(scores: Dict[str, Any]) -> Dict[str, int]:
    normalized: Dict[str, int] = {}
    for key in RUBRIC:
        normalized[key] = _clamp_score(scores.get(key, 0))
    return normalized


def _normalize_feedback(feedback: Any) -> List[str]:
    if not isinstance(feedback, list):
        return []
    result: List[str] = []
    for item in feedback:
        if isinstance(item, str) and item.strip():
            result.append(item.strip())
    return result


def evaluate_pass1(
    question: str,
    answer: str,
    _profile: Dict[str, Any] | None = None,
    temperature: float = 0.1,
) -> Dict[str, Any]:
    prompt = PASS1_TEMPLATE.format(question=question, answer=answer)
    payload, provider = _run_json_task(prompt, dict, temperature=temperature, top_p=0.8)
    scores = _normalize_scores(payload.get("scores", {}))
    feedback = _normalize_feedback(payload.get("feedback", []))
    summary = payload.get("summary", "")
    if not isinstance(summary, str):
        summary = ""
    return {
        "scores": scores,
        "feedback": feedback,
        "summary": summary.strip(),
        "provider": provider,
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
    payload, provider = _run_json_task(prompt, dict, temperature=temperature, top_p=0.8)
    raw_issues = payload.get("issues", [])
    issues = _normalize_feedback(raw_issues)
    try:
        adjustment = int(payload.get("suggested_score_adjustment", 0))
    except Exception:
        adjustment = 0
    adjustment = max(-2, min(2, adjustment))
    return {
        "issues": issues,
        "suggested_score_adjustment": adjustment,
        "provider": provider,
    }


def adjust_scores(pass1_scores: Dict[str, int], adjustment: int) -> Dict[str, int]:
    final_scores: Dict[str, int] = {}
    for key in RUBRIC:
        base = _clamp_score(pass1_scores.get(key, 0))
        final_scores[key] = _clamp_score(base + adjustment)
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
