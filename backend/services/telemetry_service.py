"""
Telemetry Service for automatic logging of evaluation metrics.

This service writes evaluation metrics to:
1. JSONL logs (for experiments)
2. PostgreSQL llm_metrics table (for dashboard queries)

Example flow:
    Candidate answer
    ↓
    STT
    ↓
    LLM evaluation
    ↓
    Save telemetry
    ↓
    Dashboard metrics
"""

import json
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from backend.db.database import AsyncSessionLocal, LLMMetrics
from backend.utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# JSONL Logging
# =========================================================

class EvaluationJSONLLogger:
    """Writes evaluation metrics to JSONL file."""
    
    def __init__(self):
        self.enabled = os.getenv("TELEMETRY_JSONL_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
        self.file_path = os.getenv(
            "TELEMETRY_LOG_PATH", "logs/evaluations.jsonl"
        )
        self._lock = threading.Lock()
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
    
    def write(self, payload: Dict[str, Any]):
        """Write evaluation metrics to JSONL file."""
        if not self.enabled:
            return
        
        record = dict(payload)
        record["timestamp"] = datetime.utcnow().isoformat()
        line = json.dumps(record, separators=(",", ":")) + "\n"
        
        with self._lock:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line)


# =========================================================
# PostgreSQL Logging
# =========================================================

class EvaluationDBLogger:
    """Writes evaluation metrics to PostgreSQL llm_metrics table."""
    
    def __init__(self):
        self.enabled = os.getenv("TELEMETRY_DB_ENABLED", "true").lower() in {
            "1", "true", "yes", "on"
        }
    
    async def write(self, payload: Dict[str, Any]):
        """Write evaluation metrics to PostgreSQL."""
        if not self.enabled:
            return
        
        try:
            from backend.db.database import AsyncSessionLocal
            async with AsyncSessionLocal() as db:
                try:
                    metric = LLMMetrics(
                        model=payload.get("model", "unknown"),
                        latency_ms=int(payload.get("latency_ms", 0)),
                        prompt_tokens=int(payload.get("prompt_tokens", 0)),
                        completion_tokens=int(payload.get("completion_tokens", 0)),
                        cost_usd=float(payload.get("cost_usd", 0.0)),
                        accuracy_score=float(payload.get("accuracy_score", 0.0)),
                        hallucination_score=float(payload.get("hallucination_score", 0.0)),
                        reasoning_score=float(payload.get("reasoning_score", 0.0)),
                        consistency_score=float(payload.get("consistency_score", 0.0)),
                        created_at=datetime.utcnow()
                    )
                    db.add(metric)
                    await db.commit()
                except Exception:
                    await db.rollback()
                    logger.exception("Telemetry DB transaction failed; rolled back")
        except Exception:
            logger.exception("Telemetry DB logging failed")


# =========================================================
# Telemetry Service
# =========================================================

class TelemetryService:
    """
    Main telemetry service that writes to both JSONL and PostgreSQL.
    
    Example usage:
        telemetry = TelemetryService()
        
        evaluation_log = {
            "model": "gpt-4",
            "latency_ms": 1500,
            "prompt_tokens": 500,
            "completion_tokens": 200,
            "cost_usd": 0.02,
            "accuracy_score": 0.85,
            "hallucination_score": 0.1,
            "reasoning_score": 0.9,
            "consistency_score": 0.88,
        }
        
        telemetry.log_evaluation(evaluation_log)
    """
    
    def __init__(self):
        self.jsonl_logger = EvaluationJSONLLogger()
        self.db_logger = EvaluationDBLogger()
    
    async def log_evaluation(self, payload: Dict[str, Any]):
        """
        Log evaluation metrics to both JSONL and PostgreSQL.
        
        Args:
            payload: Dictionary containing evaluation metrics
                - model: LLM model name
                - latency_ms: Response latency in milliseconds
                - prompt_tokens: Number of prompt tokens
                - completion_tokens: Number of completion tokens
                - cost_usd: Cost in USD
                - accuracy_score: Accuracy score (0-1)
                - hallucination_score: Hallucination risk (0-1)
                - reasoning_score: Reasoning score (0-1)
                - consistency_score: Consistency score (0-1)
        """
        # Write to JSONL
        self.jsonl_logger.write(payload)
        
        # Write to PostgreSQL
        import asyncio
        asyncio.create_task(self.db_logger.write(payload))
    
    async def log_evaluation_from_evaluation_result(
        self,
        model: str,
        latency_ms: float,
        prompt_tokens: int,
        completion_tokens: int,
        evaluation_result: Dict[str, Any],
        cost_per_1k: float = 0.0
    ):
        """
        Convenience method to log evaluation from evaluation engine result.
        
        Args:
            model: LLM model name
            latency_ms: Response latency in milliseconds
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            evaluation_result: Result from evaluation engine
            cost_per_1k: Cost per 1000 tokens
        """
        # Calculate cost
        total_tokens = prompt_tokens + completion_tokens
        cost_usd = (total_tokens / 1000.0) * cost_per_1k
        
        # Extract scores from evaluation result
        scores = evaluation_result.get("scores", {})
        technical_score = scores.get("Technical", 0.0)
        behavior_score = scores.get("Behavioral", 0.0)
        reasoning_score = scores.get("Reasoning", 0.0)
        consistency_score = scores.get("ConceptConsistency", 0.0)
        
        # Get hallucination info
        consistency = evaluation_result.get("consistency", {})
        hallucination_score = consistency.get("hallucination_risk", 0.0) / 10.0
        
        payload = {
            "model": model,
            "latency_ms": int(latency_ms),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": round(cost_usd, 6),
            "accuracy_score": round(technical_score / 10.0, 3),
            "hallucination_score": round(hallucination_score, 3),
            "reasoning_score": round(reasoning_score / 10.0, 3),
            "consistency_score": round(consistency_score / 10.0, 3),
        }
        
        await self.log_evaluation(payload)


# Singleton instance
telemetry_service = TelemetryService()


# =========================================================
# Helper Functions
# =========================================================

def get_cost_per_1k_tokens(provider: str) -> float:
    """Get cost per 1000 tokens for a provider."""
    normalized = (provider or "unknown").strip().upper().replace("-", "_")
    return float(os.getenv(f"COST_PER_1K_TOKENS_{normalized}", 
                           os.getenv("COST_PER_1K_TOKENS_DEFAULT", "0")))


def estimate_tokens(text: str) -> int:
    """Estimate token count from text."""
    words = len((text or "").split())
    return max(int(round(words * 1.3)), 0)


async def log_evaluation_metrics(
    model: str,
    latency_seconds: float,
    question: str,
    answer: str,
    evaluation_result: Dict[str, Any],
    provider: str = "unknown"
):
    """
    Convenience function to log evaluation metrics.
    
    Args:
        model: Model name
        latency_seconds: Latency in seconds
        question: Question text
        answer: Answer text
        evaluation_result: Result from evaluation engine
        provider: Provider name
    """
    # Estimate tokens
    prompt_tokens = estimate_tokens(question)
    completion_tokens = estimate_tokens(answer)
    
    # Get cost
    cost_per_1k = get_cost_per_1k_tokens(provider)
    
    # Log via telemetry service
    await telemetry_service.log_evaluation_from_evaluation_result(
        model=model,
        latency_ms=latency_seconds * 1000,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        evaluation_result=evaluation_result,
        cost_per_1k=cost_per_1k
    )

