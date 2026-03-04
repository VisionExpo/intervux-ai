import asyncio
import statistics
from collections import Counter
from typing import Any, Dict, List


class SelfConsistencyEvaluator:
    def __init__(self, passes=3):
        self.passes = max(1, int(passes))

    def evaluate(self, eval_fn, *args):
        results = []
        for _ in range(self.passes):
            result = eval_fn(*args)
            results.append(result)
        return self.aggregate(results)

    async def evaluate_parallel(self, eval_fn, *args):
        tasks = [asyncio.to_thread(eval_fn, *args) for _ in range(self.passes)]
        results = await asyncio.gather(*tasks)
        return self.aggregate(results)

    @staticmethod
    def compute_confidence(scores: List[float]) -> float:
        if not scores:
            return 0.3
        spread = max(scores) - min(scores)
        if spread <= 1:
            return 0.9
        if spread <= 3:
            return 0.6
        return 0.3

    def aggregate(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not results:
            return {
                "technical": {"accuracy": 0, "depth": 0, "problem_solving": 0},
                "behavioral": {"clarity": 0, "confidence": 0, "structure": 0},
                "hallucination_risk": 0,
                "misused_terms": [],
                "contradictions": [],
                "concept_consistency_score": 0,
                "consistency_penalty": 0.0,
                "consistency_notes": [],
                "reasoning_metrics": {
                    "logical_consistency": 0,
                    "step_completeness": 0,
                    "causal_reasoning": 0,
                },
                "reasoning_steps": [],
                "logic_flow": "unclear",
                "reasoning_score": 0.0,
                "technical_score": 0.0,
                "behavioral_score": 0.0,
                "final_score": 0.0,
                "confidence": 0.3,
                "pass_count": 0,
                "spread": 0.0,
            }

        tech_keys = ("accuracy", "depth", "problem_solving")
        beh_keys = ("clarity", "confidence", "structure")
        reasoning_keys = ("logical_consistency", "step_completeness", "causal_reasoning")

        tech_agg: Dict[str, int] = {}
        for key in tech_keys:
            values = [self._to_score(item.get("technical", {}).get(key, 0)) for item in results]
            tech_agg[key] = int(round(statistics.median(values)))

        beh_agg: Dict[str, int] = {}
        for key in beh_keys:
            values = [self._to_score(item.get("behavioral", {}).get(key, 0)) for item in results]
            beh_agg[key] = int(round(statistics.median(values)))

        reasoning_agg: Dict[str, int] = {}
        for key in reasoning_keys:
            values = [
                self._to_score(item.get("reasoning", {}).get("metrics", {}).get(key, 0))
                for item in results
            ]
            reasoning_agg[key] = int(round(statistics.median(values)))

        reasoning_score_values = [
            self._to_float(item.get("reasoning", {}).get("reasoning_score", 0.0))
            for item in results
        ]
        reasoning_score = (
            float(statistics.median(reasoning_score_values))
            if reasoning_score_values
            else 0.0
        )

        logic_flows = [
            str(item.get("reasoning", {}).get("logic_flow", "unclear")).strip().lower()
            for item in results
        ]
        logic_flow = Counter(logic_flows).most_common(1)[0][0] if logic_flows else "unclear"

        steps_counter: Counter[str] = Counter()
        for item in results:
            steps = item.get("reasoning", {}).get("steps", [])
            if not isinstance(steps, list):
                continue
            for step in steps:
                if isinstance(step, str) and step.strip():
                    steps_counter[step.strip()] += 1
        reasoning_steps = [step for step, _count in steps_counter.most_common(6)]

        tech_scores = [self._avg_scores(item.get("technical", {}), tech_keys) for item in results]
        beh_scores = [self._avg_scores(item.get("behavioral", {}), beh_keys) for item in results]
        final_scores = [self._to_float(item.get("final", 0.0)) for item in results]
        hallucination_scores = [
            self._to_score(item.get("consistency", {}).get("hallucination_risk", 0))
            for item in results
        ]
        concept_consistency_scores = [
            self._to_score(
                item.get("consistency", {}).get("concept_consistency_score", 0)
            )
            for item in results
        ]
        consistency_penalties = [
            self._to_float(item.get("consistency", {}).get("consistency_penalty", 0.0))
            for item in results
        ]

        misused_counter: Counter[str] = Counter()
        contradiction_counter: Counter[str] = Counter()
        note_counter: Counter[str] = Counter()
        for item in results:
            misused = item.get("consistency", {}).get("misused_terms", [])
            contradictions = item.get("consistency", {}).get("contradictions", [])
            notes = item.get("consistency", {}).get("notes", [])
            if isinstance(misused, list):
                for term in misused:
                    if isinstance(term, str) and term.strip():
                        misused_counter[term.strip()] += 1
            if isinstance(contradictions, list):
                for c in contradictions:
                    if isinstance(c, str) and c.strip():
                        contradiction_counter[c.strip()] += 1
            if isinstance(notes, list):
                for n in notes:
                    if isinstance(n, str) and n.strip():
                        note_counter[n.strip()] += 1

        tech_med = float(statistics.median(tech_scores)) if tech_scores else 0.0
        beh_med = float(statistics.median(beh_scores)) if beh_scores else 0.0
        final_med = float(statistics.median(final_scores)) if final_scores else 0.0

        confidence = self.compute_confidence(final_scores or [final_med])
        spread = (max(final_scores) - min(final_scores)) if final_scores else 0.0

        return {
            "technical": tech_agg,
            "behavioral": beh_agg,
            "hallucination_risk": int(round(statistics.median(hallucination_scores)))
            if hallucination_scores
            else 0,
            "misused_terms": [s for s, _ in misused_counter.most_common(6)],
            "contradictions": [s for s, _ in contradiction_counter.most_common(6)],
            "concept_consistency_score": int(
                round(statistics.median(concept_consistency_scores))
            )
            if concept_consistency_scores
            else 0,
            "consistency_penalty": round(
                float(statistics.median(consistency_penalties))
                if consistency_penalties
                else 0.0,
                2,
            ),
            "consistency_notes": [s for s, _ in note_counter.most_common(8)],
            "reasoning_metrics": reasoning_agg,
            "reasoning_steps": reasoning_steps,
            "logic_flow": logic_flow,
            "reasoning_score": round(reasoning_score, 2),
            "technical_score": round(tech_med, 2),
            "behavioral_score": round(beh_med, 2),
            "final_score": round(final_med, 2),
            "confidence": round(confidence, 2),
            "pass_count": len(results),
            "spread": round(spread, 3),
        }

    @staticmethod
    def _to_score(value: Any) -> int:
        try:
            parsed = int(round(float(value)))
        except Exception:
            parsed = 0
        return max(0, min(10, parsed))

    @staticmethod
    def _to_float(value: Any) -> float:
        try:
            return float(value)
        except Exception:
            return 0.0

    def _avg_scores(self, values: Dict[str, Any], keys: tuple[str, ...]) -> float:
        nums = [self._to_score(values.get(key, 0)) for key in keys]
        if not nums:
            return 0.0
        return sum(nums) / float(len(nums))
