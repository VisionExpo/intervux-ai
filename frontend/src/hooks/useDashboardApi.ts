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
    setIsLoading(true);
    setError(null);
    try {
      const result = await authFetch<T>(path);
      setData(result);
    } catch (err) {
      setError(handleApiError(err));
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

