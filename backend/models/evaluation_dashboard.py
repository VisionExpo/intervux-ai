from __future__ import annotations

from pydantic import BaseModel


class LatencyMetrics(BaseModel):
    p50: float
    p95: float
    p99: float


class ThroughputMetrics(BaseModel):
    requests_per_second: float
    tokens_per_second: float


class ModelQualityMetrics(BaseModel):
    accuracy: float
    hallucination_rate: float
    consistency_score: float
    reasoning_score: float


class PerformanceMetrics(BaseModel):
    latency: LatencyMetrics
    throughput: ThroughputMetrics
    error_rate: float


class CostByModel(BaseModel):
    model: str
    cost: float


class CostMetrics(BaseModel):
    average_cost_per_request: float
    daily_ai_spend: float
    cost_by_model: list[CostByModel]


class TokenUsageMetrics(BaseModel):
    average_prompt_tokens: float
    average_completion_tokens: float
    total_tokens_today: int


class ModelUsageMetric(BaseModel):
    model: str
    percentage: float
    requests: int


class SkillMetric(BaseModel):
    skill: str
    score: float


class InterviewMetrics(BaseModel):
    candidate_success_rate: float
    average_interview_duration_minutes: float
    skill_evaluation_distribution: list[SkillMetric]


class SystemHealthMetrics(BaseModel):
    active_interview_sessions: float
    queue_length: float
    gpu_memory_allocated_mb: float
    gpu_memory_reserved_mb: float
    max_concurrent_sessions: float


class AlertItem(BaseModel):
    severity: str
    message: str


class EvaluationDashboardResponse(BaseModel):
    generated_at: str
    model_quality: ModelQualityMetrics
    performance: PerformanceMetrics
    cost: CostMetrics
    token_usage: TokenUsageMetrics
    model_usage: list[ModelUsageMetric]
    interview_metrics: InterviewMetrics
    system_health: SystemHealthMetrics
    alerts: list[AlertItem]
    ai_hiring_summary: str


class ExperimentCreateRequest(BaseModel):
    experiment_name: str
    model_version: str
    prompt_template: str
    accuracy: float | None = None
    latency_ms: int | None = None
