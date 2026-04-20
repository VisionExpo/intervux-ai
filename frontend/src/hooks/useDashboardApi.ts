/**
 * Shared API hooks for fetching dashboard data with loading/error states.
 * Each hook follows the pattern: { data, isLoading, error, refetch }
 */
import { useCallback, useEffect, useState } from 'react';
import { authFetch } from './authFetch';

// ──────────────────────────────────────────
// Generic fetch wrapper
// ──────────────────────────────────────────
interface UseFetchResult<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => void;
}

// ──────────────────────────────────────────
// Mock Data for Demo Mode
// ──────────────────────────────────────────
// eslint-disable-next-line @typescript-eslint/no-explicit-any -- Mock data intentionally uses broad types for demo fallback
const MOCK_DATA: Record<string, any> = {
  '/api/candidate/dashboard': {
    profile_score: 82,
    resume_score: 75,
    mock_interview_score: 88,
    mock_interviews_remaining: 3,
    recent_activity: ['Resume uploaded', 'Mock interview completed', 'Profile updated'],
  },
  '/api/candidate/profile': {
    id: 1,
    user_id: 'demo-123',
    name: 'Demo Candidate',
    skills: ['React', 'TypeScript', 'Node.js', 'Python'],
    resume_url: 'https://example.com/resume.pdf',
    profile_score: 82,
    created_at: new Date().toISOString(),
  },
  '/api/candidates': [
    { id: '1', name: 'Alice Smith', email: 'alice@example.com', role: 'Frontend Developer', created_at: new Date().toISOString() },
    { id: '2', name: 'Bob Johnson', email: 'bob@example.com', role: 'Backend Engineer', created_at: new Date().toISOString(), interview_id: 'int-1' },
    { id: '3', name: 'Charlie Brown', email: 'charlie@example.com', role: 'Fullstack Dev', created_at: new Date().toISOString() },
  ],
  '/api/job-posts': [
    { id: 'j1', title: 'Senior React Developer', status: 'active', experience_level: 'Senior', created_at: new Date().toISOString() },
    { id: 'j2', title: 'Python Backend Engineer', status: 'active', experience_level: 'Mid', created_at: new Date().toISOString() },
    { id: 'j3', title: 'UX Designer', status: 'paused', experience_level: 'Lead', created_at: new Date().toISOString() },
  ],
  '/api/admin/evaluation-dashboard': {
    generated_at: new Date().toISOString(),
    model_quality: {
      accuracy: 0.94,
      hallucination_rate: 0.02,
      consistency_score: 0.89,
      reasoning_score: 0.91,
    },
    performance: {
      latency: { p50: 450, p95: 1200, p99: 2500 },
      throughput: { requests_per_second: 12.5, tokens_per_second: 450 },
      error_rate: 0.005,
    },
    cost: {
      total_spend_usd: 145.50,
      average_cost_per_request: 0.012,
      daily_ai_spend: 145.5,
      cost_by_model: [
        { model: 'GPT-4o', cost: 85.2 },
        { model: 'Gemini 1.5 Pro', cost: 60.3 },
      ],
    },
    token_usage: {
      average_prompt_tokens: 1200,
      average_completion_tokens: 450,
      total_tokens_today: 1250000,
    },
    model_usage: [
      { model: 'GPT-4o', percentage: 65, requests: 850 },
      { model: 'Gemini 1.5 Pro', percentage: 35, requests: 460 },
    ],
    interview_metrics: {
      candidate_success_rate: 0.76,
      average_interview_duration_minutes: 42,
      skill_evaluation_distribution: [
        { skill: 'Problem Solving', score: 8.5 },
        { skill: 'Technical Depth', score: 7.9 },
      ],
    },
    system_health: {
      active_interview_sessions: 24,
      queue_length: 3,
      gpu_memory_allocated_mb: 4096,
      gpu_memory_reserved_mb: 8192,
      max_concurrent_sessions: 100,
    },
    alerts: [
      { severity: 'high', message: 'Spike in p95 latency detected in us-east-1' },
      { severity: 'medium', message: 'Budget alert: 15% of daily limit reached' },
    ],
    ai_hiring_summary: 'Overall recruitment efficiency is up 12%.'
  }
};

function handleApiError(err: unknown): string {
  if (err instanceof Error) {
    if (err.message.includes('401')) return 'Session expired. Please log in again.';
    if (err.message.includes('403')) return 'Permission denied for this dashboard.';
    if (err.message.includes('500')) return 'Server overload. Retrying soon...';
    if (err.message === 'Failed to fetch') return 'Network lost. Check your connection.';
    return err.message;
  }
  return 'An unexpected error occurred';
}

/**
 * Currency Formatter for Admin costs
 */
export const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
  }).format(value);
};

/**
 * Percentage Formatter
 */
export const formatPercent = (value: number) => {
  return `${(value * 100).toFixed(1)}%`;
};

function useApiFetch<T>(path: string): UseFetchResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    const isMock = window.location.hash.includes('mock=true');
    setIsLoading(true);
    setError(null);
    try {
      const result = await authFetch<T>(path);
      setData(result);
    } catch (err) {
      if (isMock && MOCK_DATA[path]) {
        console.warn(`[API MOCK] Falling back to mock data for ${path}`);
        setData(MOCK_DATA[path] as T);
      } else {
        setError(handleApiError(err));
      }
    } finally {
      setIsLoading(false);
    }
  }, [path]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  return { data, isLoading, error, refetch: fetchData };
}

// ──────────────────────────────────────────
// Candidate hooks
// ──────────────────────────────────────────
export interface CandidateDashboardData {
  profile_score: number;
  resume_score: number;
  mock_interview_score: number;
  mock_interviews_remaining: number;
  recent_activity: string[];
}

export interface CandidateProfileData {
  id: number;
  user_id: string;
  name: string;
  skills: string[];
  experience_years: number | null;
  education: string | null;
  resume_url: string | null;
  resume_score: number | null;
  interview_score: number | null;
  profile_score: number;
  github_url: string | null;
  linkedin_url: string | null;
  mock_interviews_remaining: number;
  created_at: string;
}

export function useCandidateDashboard() {
  return useApiFetch<CandidateDashboardData>('/api/candidate/dashboard');
}

export function useCandidateProfile() {
  return useApiFetch<CandidateProfileData>('/api/candidate/profile');
}

// ──────────────────────────────────────────
// Recruiter hooks
// ──────────────────────────────────────────
export interface RecruiterCandidate {
  id: string;
  name: string;
  email: string;
  role: string;
  resume_url: string;
  created_at: string;
  interview_id?: string;
}

export interface RecruiterJobPost {
  id: string;
  title: string;
  description: string;
  required_skills: string[];
  experience_level: string;
  status: string;
  created_at: string;
}

export function useRecruiterCandidates() {
  return useApiFetch<RecruiterCandidate[]>('/api/candidates');
}

export function useRecruiterJobPosts() {
  return useApiFetch<RecruiterJobPost[]>('/api/job-posts');
}

// ──────────────────────────────────────────
// Admin hooks
// ──────────────────────────────────────────
import type { EvaluationDashboardResponse } from '../types';

export function useAdminEvaluationDashboard() {
  return useApiFetch<EvaluationDashboardResponse>('/api/admin/evaluation-dashboard');
}

export interface AdminMetricsAggregates {
  total_interviews: number;
  total_candidates: number;
  total_recruiters: number;
  avg_score: number;
  active_sessions?: number;
  completion_rate?: number;
}

export function useAdminMetricsAggregates() {
  return useApiFetch<AdminMetricsAggregates>('/api/admin/metrics/aggregates');
}

export interface AdminMetricsTrend {
  date: string;
  interviews: number;
  candidates: number;
}

export function useAdminMetricsTrends(days = 30) {
  return useApiFetch<AdminMetricsTrend[]>(`/api/admin/metrics/trends?days=${days}`);
}
