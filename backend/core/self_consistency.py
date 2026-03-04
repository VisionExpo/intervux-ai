import asyncio
import statistics
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
                "technical_score": 0.0,
                "behavioral_score": 0.0,
                "final_score": 0.0,
                "confidence": 0.3,
                "pass_count": 0,
                "spread": 0.0,
            }

        tech_keys = ("accuracy", "depth", "problem_solving")
        beh_keys = ("clarity", "confidence", "structure")

        tech_agg: Dict[str, int] = {}
        for key in tech_keys:
            values = [self._to_score(item.get("technical", {}).get(key, 0)) for item in results]
            tech_agg[key] = int(round(statistics.median(values)))

        beh_agg: Dict[str, int] = {}
        for key in beh_keys:
            values = [self._to_score(item.get("behavioral", {}).get(key, 0)) for item in results]
            beh_agg[key] = int(round(statistics.median(values)))

        tech_scores = [self._avg_scores(item.get("technical", {}), tech_keys) for item in results]
        beh_scores = [self._avg_scores(item.get("behavioral", {}), beh_keys) for item in results]
        final_scores = [self._to_float(item.get("final", 0.0)) for item in results]

        tech_med = float(statistics.median(tech_scores)) if tech_scores else 0.0
        beh_med = float(statistics.median(beh_scores)) if beh_scores else 0.0
        final_med = float(statistics.median(final_scores)) if final_scores else 0.0

        confidence = self.compute_confidence(final_scores or [final_med])
        spread = (max(final_scores) - min(final_scores)) if final_scores else 0.0

        return {
            "technical": tech_agg,
            "behavioral": beh_agg,
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
