export type DashboardTab = "candidates" | "interviews" | "analytics" | "evaluation";

export interface CandidateListItem {
  id: string;
  name: string;
  email: string;
  role: string;
  resume_url: string;
  created_at: string;
  interview_id?: string;
}

export interface InterviewScoreCard {
  id: string;
  candidate_id: string;
  role: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  started_at: string;
  completed_at: string;
}

export interface InterviewQuestion {
  id: string;
  interview_id: string;
  question: string;
  answer: string;
  score: number;
  feedback: string;
}

export interface ReplaySegment {
  question: string;
  candidate_audio: string;
  transcript: string;
  evaluation: {
    technical: number;
    clarity: number;
    reasoning: number;
  };
}

export interface CandidateInterviewReport {
  candidate: CandidateListItem;
  interview: InterviewScoreCard;
  questions: InterviewQuestion[];
  replay_segments: ReplaySegment[];
}

export interface SkillAnalyticsResponse {
  interview_id: string;
  skills: Record<string, number>;
}

export interface CandidateComparisonRow {
  candidate_id: string;
  candidate_name: string;
  technical: number;
  communication: number;
  overall: number;
}

export interface LatencyMetrics {
  p50: number;
  p95: number;
  p99: number;
}

export interface ThroughputMetrics {
  requests_per_second: number;
  tokens_per_second: number;
}

export interface ModelQualityMetrics {
  accuracy: number;
  hallucination_rate: number;
  consistency_score: number;
  reasoning_score: number;
}

export interface PerformanceMetrics {
  latency: LatencyMetrics;
  throughput: ThroughputMetrics;
  error_rate: number;
}

export interface CostByModel {
  model: string;
  cost: number;
}

export interface CostMetrics {
  average_cost_per_request: number;
  daily_ai_spend: number;
  cost_by_model: CostByModel[];
}

export interface TokenUsageMetrics {
  average_prompt_tokens: number;
  average_completion_tokens: number;
  total_tokens_today: number;
}

export interface ModelUsageMetric {
  model: string;
  percentage: number;
  requests: number;
}

export interface SkillMetric {
  skill: string;
  score: number;
}

export interface InterviewMetrics {
  candidate_success_rate: number;
  average_interview_duration_minutes: number;
  skill_evaluation_distribution: SkillMetric[];
}

export interface SystemHealthMetrics {
  active_interview_sessions: number;
  queue_length: number;
  gpu_memory_allocated_mb: number;
  gpu_memory_reserved_mb: number;
  max_concurrent_sessions: number;
}

export interface AlertItem {
  severity: string;
  message: string;
}

export interface EvaluationDashboardResponse {
  generated_at: string;
  model_quality: ModelQualityMetrics;
  performance: PerformanceMetrics;
  cost: CostMetrics;
  token_usage: TokenUsageMetrics;
  model_usage: ModelUsageMetric[];
  interview_metrics: InterviewMetrics;
  system_health: SystemHealthMetrics;
  alerts: AlertItem[];
  ai_hiring_summary: string;
}
