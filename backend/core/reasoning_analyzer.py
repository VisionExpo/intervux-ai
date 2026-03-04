from __future__ import annotations

from typing import Any, Dict, List

from backend.core.llm_brain import _run_json_task

EXTRACT_REASONING_TEMPLATE = """
Extract reasoning steps from the answer.
Return JSON:
{
  "steps": ["..."],
  "logic_flow": "clear"
}
Answer: {answer}
""".strip()

EVALUATE_REASONING_TEMPLATE = """
Evaluate reasoning quality.
Return JSON:
{
  "logical_consistency": 0,
  "step_completeness": 0,
  "causal_reasoning": 0
}
Question: {question}
Reasoning Steps: {steps_json}
Logic Flow: {logic_flow}
""".strip()


def _clamp_score(value: Any) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = 0
    return max(0, min(10, parsed))


def _normalize_logic_flow(value: Any) -> str:
    if not isinstance(value, str):
        return "unclear"
    normalized = value.strip().lower()
    if normalized in {"clear", "partial", "unclear"}:
        return normalized
    return "unclear"


class ReasoningAnalyzer:
    def extract_reasoning(self, answer: str) -> Dict[str, Any]:
        prompt = EXTRACT_REASONING_TEMPLATE.format(answer=answer)
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
        raw_steps = payload.get("steps", [])
        steps: List[str] = []
        if isinstance(raw_steps, list):
            for item in raw_steps:
                if isinstance(item, str) and item.strip():
                    steps.append(item.strip())
        logic_flow = _normalize_logic_flow(payload.get("logic_flow", "unclear"))
        return {"steps": steps[:8], "logic_flow": logic_flow}

    def evaluate_reasoning(self, question: str, reasoning: Dict[str, Any]) -> Dict[str, int]:
        prompt = EVALUATE_REASONING_TEMPLATE.format(
            question=question,
            steps_json=reasoning.get("steps", []),
            logic_flow=reasoning.get("logic_flow", "unclear"),
        )
        payload, _provider = _run_json_task(prompt, dict, temperature=0.1, top_p=0.8)
        return {
            "logical_consistency": _clamp_score(payload.get("logical_consistency", 0)),
            "step_completeness": _clamp_score(payload.get("step_completeness", 0)),
            "causal_reasoning": _clamp_score(payload.get("causal_reasoning", 0)),
        }

    @staticmethod
    def compute_reasoning_score(metrics: Dict[str, int]) -> float:
        if not metrics:
            return 0.0
        return round(sum(metrics.values()) / float(len(metrics)), 2)

    def analyze(self, question: str, answer: str) -> Dict[str, Any]:
        reasoning = self.extract_reasoning(answer)
        metrics = self.evaluate_reasoning(question, reasoning)
        reasoning_score = self.compute_reasoning_score(metrics)
        return {
            "steps": reasoning.get("steps", []),
            "logic_flow": reasoning.get("logic_flow", "unclear"),
            "metrics": metrics,
            "reasoning_score": reasoning_score,
        }
