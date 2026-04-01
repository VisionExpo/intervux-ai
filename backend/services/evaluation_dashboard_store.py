from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.infrastructure.database.database import LLMMetrics, Experiment
from backend.models.evaluation_dashboard import (
    AlertItem,
    CostByModel,
    CostMetrics,
    EvaluationDashboardResponse,
    InterviewMetrics,
    LatencyMetrics,
    ModelQualityMetrics,
    ModelUsageMetric,
    PerformanceMetrics,
    SkillMetric,
    SystemHealthMetrics,
    ThroughputMetrics,
    TokenUsageMetrics,
)
from backend.models.recruiter_dashboard_models import Interview
from backend.utils.metrics import metrics


def _read_jsonl_records() -> list[dict[str, Any]]:
    file_path = Path(os.getenv("RESEARCH_LOG_PATH", "logs/research/evaluator_dataset.jsonl"))
    if not file_path.exists():
        return []

    records: list[dict[str, Any]] = []
    with file_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            raw = line.strip()
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
    return records


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _estimate_tokens(text: str) -> int:
    words = len((text or "").split())
    return max(int(round(words * 1.3)), 0)


def _normalize_ten_point(value: Any) -> float:
    score = max(0.0, min(_to_float(value, 0.0), 10.0))
    return round(score / 10.0, 3)


def _provider_cost_per_1k(provider: str) -> float:
    normalized = (provider or "unknown").strip().upper().replace("-", "_")
    return _to_float(
        os.getenv(f"COST_PER_1K_TOKENS_{normalized}", os.getenv("COST_PER_1K_TOKENS_DEFAULT", "0")),
        0.0,
    )


def _today_timestamp() -> float:
    return datetime.now().timestamp()


async def get_evaluation_dashboard(db: AsyncSession) -> EvaluationDashboardResponse:
    records = _read_jsonl_records()
    snapshot = metrics.snapshot()
    now = datetime.now()
    day_start = datetime(now.year, now.month, now.day).timestamp()

    scores = [_to_float(item.get("score")) for item in records]
    reasoning_scores = [_to_float(item.get("reasoning_score")) for item in records]
    concept_consistency_scores = [
        _to_float(item.get("concept_consistency_score")) for item in records
    ]
    hallucination_risks = [_to_float(item.get("hallucination_risk")) for item in records]

    model_quality = ModelQualityMetrics(
        accuracy=round(mean(_normalize_ten_point(score) for score in scores), 3) if scores else 0.0,
        hallucination_rate=round(
            (
                sum(1 for risk in hallucination_risks if risk >= 6.0)
                / float(len(hallucination_risks))
                * 100.0
            ),
            2,
        )
        if hallucination_risks
        else 0.0,
        consistency_score=round(
            mean(_normalize_ten_point(score) for score in concept_consistency_scores),
            3,
        )
        if concept_consistency_scores
        else 0.0,
        reasoning_score=round(
            mean(_normalize_ten_point(score) for score in reasoning_scores),
            3,
        )
        if reasoning_scores
        else 0.0,
    )

    latency_snapshot = snapshot.get("latency_percentiles", {}).get("request_total", {})
    answer_cycle_latencies = [_to_float(item.get("time_taken")) for item in records if item.get("time_taken") is not None]
    total_processing_seconds = sum(latency for latency in answer_cycle_latencies if latency > 0)

    if len(records) >= 2:
        timestamps = sorted(_to_float(item.get("timestamp")) for item in records if item.get("timestamp") is not None)
        observed_span = max(timestamps[-1] - timestamps[0], 1.0) if len(timestamps) >= 2 else 1.0
    else:
        observed_span = max(total_processing_seconds, 1.0)

    total_prompt_tokens = sum(_estimate_tokens(str(item.get("question", ""))) for item in records)
    total_completion_tokens = sum(_estimate_tokens(str(item.get("answer", ""))) for item in records)
    total_tokens = total_prompt_tokens + total_completion_tokens

    request_count = int(snapshot.get("request", 0))
    error_count = int(snapshot.get("error", 0))
    error_rate = round((error_count / float(request_count) * 100.0), 2) if request_count else 0.0

    performance = PerformanceMetrics(
        latency=LatencyMetrics(
            p50=round(_to_float(latency_snapshot.get("p50")), 3),
            p95=round(_to_float(latency_snapshot.get("p95")), 3),
            p99=round(_to_float(latency_snapshot.get("p99")), 3),
        ),
        throughput=ThroughputMetrics(
            requests_per_second=round(len(records) / observed_span, 3) if records else 0.0,
            tokens_per_second=round(total_tokens / total_processing_seconds, 3)
            if total_processing_seconds
            else 0.0,
        ),
        error_rate=error_rate,
    )

    provider_counts: Counter[str] = Counter()
    provider_costs: defaultdict[str, float] = defaultdict(float)
    request_costs: list[float] = []
    todays_total_tokens = 0
    todays_request_cost = 0.0

    for item in records:
        provider = str(item.get("provider") or "unknown")
        provider_counts[provider] += 1

        prompt_tokens = _estimate_tokens(str(item.get("question", "")))
        completion_tokens = _estimate_tokens(str(item.get("answer", "")))
        request_tokens = prompt_tokens + completion_tokens
        request_cost = round((request_tokens / 1000.0) * _provider_cost_per_1k(provider), 6)
        provider_costs[provider] += request_cost
        request_costs.append(request_cost)

        if _to_float(item.get("timestamp")) >= day_start:
            todays_total_tokens += request_tokens
            todays_request_cost += request_cost

    cost = CostMetrics(
        average_cost_per_request=round(mean(request_costs), 6) if request_costs else 0.0,
        daily_ai_spend=round(todays_request_cost, 4),
        cost_by_model=[
            CostByModel(model=provider, cost=round(amount, 4))
            for provider, amount in sorted(provider_costs.items(), key=lambda item: item[1], reverse=True)
        ],
    )

    today_records = [item for item in records if _to_float(item.get("timestamp")) >= day_start]
    token_usage = TokenUsageMetrics(
        average_prompt_tokens=round(
            mean(_estimate_tokens(str(item.get("question", ""))) for item in records), 2
        )
        if records
        else 0.0,
        average_completion_tokens=round(
            mean(_estimate_tokens(str(item.get("answer", ""))) for item in records), 2
        )
        if records
        else 0.0,
        total_tokens_today=sum(
            _estimate_tokens(str(item.get("question", ""))) + _estimate_tokens(str(item.get("answer", "")))
            for item in today_records
        ),
    )

    total_model_requests = sum(provider_counts.values())
    model_usage = [
        ModelUsageMetric(
            model=provider,
            percentage=round((count / float(total_model_requests)) * 100.0, 2),
            requests=count,
        )
        for provider, count in provider_counts.most_common()
    ]

    res = await db.execute(select(Interview))
    interviews = res.scalars().all()
    successful_interviews = [
        interview for interview in interviews if _to_float(interview.overall_score) >= 80.0
    ]
    completed_durations = []
    for interview in interviews:
        if interview.started_at and interview.completed_at:
            completed_durations.append(
                max((interview.completed_at - interview.started_at).total_seconds() / 60.0, 0.0)
            )

    skill_scores: defaultdict[str, list[float]] = defaultdict(list)
    for item in records:
        skill = str(item.get("skill") or "Unknown")
        if not skill.strip():
            skill = "Unknown"
        score = item.get("skill_mastery_score")
        if score is None:
            score = item.get("score")
        skill_scores[skill].append(_to_float(score))

    interview_metrics = InterviewMetrics(
        candidate_success_rate=round(
            (len(successful_interviews) / float(len(interviews)) * 100.0), 2
        )
        if interviews
        else 0.0,
        average_interview_duration_minutes=round(mean(completed_durations), 2)
        if completed_durations
        else 0.0,
        skill_evaluation_distribution=[
            SkillMetric(skill=skill, score=round(mean(values), 2))
            for skill, values in sorted(
                skill_scores.items(),
                key=lambda item: mean(item[1]) if item[1] else 0.0,
                reverse=True,
            )
        ],
    )

    gauges = snapshot.get("gauges", {})
    system_health = SystemHealthMetrics(
        active_interview_sessions=round(_to_float(gauges.get("active_sessions")), 2),
        queue_length=round(_to_float(gauges.get("queue_depth")), 2),
        gpu_memory_allocated_mb=round(_to_float(gauges.get("gpu_memory_allocated_mb")), 2),
        gpu_memory_reserved_mb=round(_to_float(gauges.get("gpu_memory_reserved_mb")), 2),
        max_concurrent_sessions=round(_to_float(gauges.get("max_concurrent_sessions")), 2),
    )

    alerts: list[AlertItem] = []
    latency_threshold = _to_float(os.getenv("ALERT_LATENCY_P95_S", "3"), 3.0)
    error_threshold = _to_float(os.getenv("ALERT_ERROR_RATE_PCT", "2"), 2.0)
    spend_threshold = _to_float(os.getenv("ALERT_DAILY_COST", "500"), 500.0)
    queue_threshold = _to_float(os.getenv("ALERT_QUEUE_LENGTH", "5"), 5.0)

    if performance.latency.p95 > latency_threshold:
        alerts.append(AlertItem(severity="high", message=f"p95 latency is {performance.latency.p95:.2f}s"))
    if performance.error_rate > error_threshold:
        alerts.append(AlertItem(severity="high", message=f"error rate is {performance.error_rate:.2f}%"))
    if cost.daily_ai_spend > spend_threshold:
        alerts.append(AlertItem(severity="medium", message=f"daily AI spend is ${cost.daily_ai_spend:.2f}"))
    if system_health.queue_length > queue_threshold:
        alerts.append(AlertItem(severity="medium", message=f"queue length is {system_health.queue_length:.0f}"))

    if not alerts:
        alerts.append(AlertItem(severity="info", message="All monitored thresholds are currently healthy."))

    summary_bits = [
        f"Accuracy is {model_quality.accuracy:.2f} with hallucination rate at {model_quality.hallucination_rate:.1f}%.",
        f"p95 latency is {performance.latency.p95:.2f}s and interview pass rate is {interview_metrics.candidate_success_rate:.1f}%.",
    ]
    if interview_metrics.skill_evaluation_distribution:
        top_skill = interview_metrics.skill_evaluation_distribution[0]
        summary_bits.append(f"Strongest evaluated skill is {top_skill.skill} at {top_skill.score:.2f}.")

    return EvaluationDashboardResponse(
        generated_at=now.isoformat(),
        model_quality=model_quality,
        performance=performance,
        cost=cost,
        token_usage=token_usage,
        model_usage=model_usage,
        interview_metrics=interview_metrics,
        system_health=system_health,
        alerts=alerts,
        ai_hiring_summary=" ".join(summary_bits),
    )


# =========================================================
# PostgreSQL Metrics Query Functions
# =========================================================

async def get_llm_metrics_from_db(
    db: AsyncSession,
    days: Optional[int] = None,
    model: Optional[str] = None
) -> list[LLMMetrics]:
    """
    Query llm_metrics from PostgreSQL.
    
    Args:
        db: Database session
        days: Optional number of days to look back
        model: Optional model name filter
        
    Returns:
        List of LLMMetrics records
    """
    query = select(LLMMetrics)
    
    if days is not None:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(LLMMetrics.created_at >= cutoff)
    
    if model:
        query = query.filter(LLMMetrics.model == model)
    
    res = await db.execute(query.order_by(LLMMetrics.created_at.desc()))
    return res.scalars().all()


async def get_db_metrics_aggregates(db: AsyncSession) -> dict[str, Any]:
    """
    Get aggregated metrics from PostgreSQL llm_metrics table.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary containing aggregated metrics
    """
    # Get last 24 hours of metrics
    cutoff_24h = datetime.utcnow() - timedelta(hours=24)
    cutoff_7d = datetime.utcnow() - timedelta(days=7)
    cutoff_30d = datetime.utcnow() - timedelta(days=30)
    
    # Query metrics
    res_24h = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_24h))
    metrics_24h = res_24h.scalars().all()
    
    res_7d = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_7d))
    metrics_7d = res_7d.scalars().all()
    
    res_30d = await db.execute(select(LLMMetrics).filter(LLMMetrics.created_at >= cutoff_30d))
    metrics_30d = res_30d.scalars().all()
    
    # Aggregate by model
    def aggregate_metrics(metrics_list: list[LLMMetrics]) -> dict[str, Any]:
        if not metrics_list:
            return {
                "count": 0,
                "avg_latency_ms": 0,
                "total_tokens": 0,
                "total_cost_usd": 0,
                "avg_accuracy": 0,
                "avg_hallucination": 0,
            }
        
        total_latency = sum(m.latency_ms for m in metrics_list)
        total_prompt = sum(m.prompt_tokens for m in metrics_list)
        total_completion = sum(m.completion_tokens for m in metrics_list)
        total_cost = sum(m.cost_usd for m in metrics_list)
        accuracies = [m.accuracy_score for m in metrics_list if m.accuracy_score]
        hallucinations = [m.hallucination_score for m in metrics_list if m.hallucination_score]
        
        return {
            "count": len(metrics_list),
            "avg_latency_ms": total_latency / len(metrics_list) if metrics_list else 0,
            "total_tokens": total_prompt + total_completion,
            "total_cost_usd": total_cost,
            "avg_accuracy": mean(accuracies) if accuracies else 0,
            "avg_hallucination": mean(hallucinations) if hallucinations else 0,
        }
    
    # Model breakdown
    model_breakdown = defaultdict(lambda: {"count": 0, "total_cost": 0.0})
    for m in metrics_24h:
        model_breakdown[m.model]["count"] += 1
        model_breakdown[m.model]["total_cost"] += m.cost_usd
    
    return {
        "last_24h": aggregate_metrics(metrics_24h),
        "last_7d": aggregate_metrics(metrics_7d),
        "last_30d": aggregate_metrics(metrics_30d),
        "model_breakdown_24h": dict(model_breakdown),
    }


async def get_historical_trends(db: AsyncSession, days: int = 30) -> dict[str, Any]:
    """
    Get historical trend data for charts.
    
    Args:
        db: Database session
        days: Number of days to look back
        
    Returns:
        Dictionary containing trend data
    """
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Get daily aggregates
    query = select(
        func.date(LLMMetrics.created_at).label("date"),
        func.avg(LLMMetrics.latency_ms).label("avg_latency"),
        func.avg(LLMMetrics.accuracy_score).label("avg_accuracy"),
        func.avg(LLMMetrics.hallucination_score).label("avg_hallucination"),
        func.sum(LLMMetrics.cost_usd).label("total_cost"),
        func.count(LLMMetrics.id).label("request_count"),
    ).filter(
        LLMMetrics.created_at >= cutoff
    ).group_by(
        func.date(LLMMetrics.created_at)
    ).order_by(
        func.date(LLMMetrics.created_at)
    )
    res = await db.execute(query)
    daily_metrics = res.all()
    
    trends = {
        "dates": [],
        "latency": [],
        "accuracy": [],
        "hallucination": [],
        "cost": [],
        "requests": [],
    }
    
    for row in daily_metrics:
        trends["dates"].append(str(row.date))
        trends["latency"].append(round(row.avg_latency or 0, 2))
        trends["accuracy"].append(round(row.avg_accuracy or 0, 3))
        trends["hallucination"].append(round(row.avg_hallucination or 0, 3))
        trends["cost"].append(round(row.total_cost or 0, 4))
        trends["requests"].append(row.request_count)
    
    return trends


# =========================================================
# Experiment Tracking Functions
# =========================================================

async def log_experiment(
    db: AsyncSession,
    experiment_name: str,
    model_version: str,
    prompt_template: str,
    accuracy: Optional[float] = None,
    latency_ms: Optional[int] = None
) -> Experiment:
    """
    Log an experiment result.
    
    Args:
        db: Database session
        experiment_name: Name of the experiment
        model_version: Model version used
        prompt_template: Prompt template used
        accuracy: Optional accuracy score
        latency_ms: Optional latency in ms
        
    Returns:
        Created Experiment record
    """
    experiment = Experiment(
        experiment_name=experiment_name,
        model_version=model_version,
        prompt_template=prompt_template,
        accuracy=accuracy,
        latency_ms=latency_ms,
    )
    db.add(experiment)
    await db.commit()
    await db.refresh(experiment)
    return {
        "id": experiment.id,
        "experiment_name": experiment.experiment_name,
        "model_version": experiment.model_version,
        "prompt_template": experiment.prompt_template,
        "accuracy": experiment.accuracy,
        "latency_ms": experiment.latency_ms,
        "created_at": experiment.created_at
    }


async def get_experiments(db: AsyncSession, limit: int = 100) -> list[Experiment]:
    """
    Get experiment results.
    
    Args:
        db: Database session
        limit: Maximum number of results
        
    Returns:
        List of Experiment records
    """
    res = await db.execute(select(Experiment).order_by(
        Experiment.created_at.desc()
    ).limit(limit))
    return res.scalars().all()


async def compare_experiments(db: AsyncSession, experiment_names: list[str]) -> dict[str, Any]:
    """
    Compare multiple experiments.
    
    Args:
        db: Database session
        experiment_names: List of experiment names to compare
        
    Returns:
        Dictionary containing comparison data
    """
    res = await db.execute(select(Experiment).filter(
        Experiment.experiment_name.in_(experiment_names)
    ))
    experiments = res.scalars().all()
    
    comparison = {}
    for exp in experiments:
        comparison[exp.experiment_name] = {
            "model_version": exp.model_version,
            "accuracy": exp.accuracy,
            "latency_ms": exp.latency_ms,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
        }
    
    return comparison
