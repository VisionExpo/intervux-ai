import { useEffect, useState } from "react";
import { authFetch } from "./authFetch";
import { API } from "../config/api";

type DashboardState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

// Candidate Dashboard Hook
export interface CandidateDashboardData {
  profile_score: number;
  resume_score: number;
  mock_interview_score: number;
  mock_interviews_remaining: number;
  recent_activity: string[];
}

export function useCandidateDashboard() {
  const [state, setState] = useState<DashboardState<CandidateDashboardData>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;
    const fetchDashboard = async () => {
      try {
        const url = `${API.candidates}/dashboard`;
        const data = await authFetch<CandidateDashboardData>(url);
        if (mounted) setState({ data, loading: false, error: null });
      } catch (err) {
        if (mounted) setState({ data: null, loading: false, error: (err as Error).message });
      }
    };
    fetchDashboard();
    return () => { mounted = false; };
  }, []);

  return state;
}

// Recruiter Dashboard Hook
export interface CandidateSummary {
  name: string;
  role: string;
  score: number;
  stage: string;
}

export interface RecruiterDashboardData {
  candidates: any[];
  stats: {
    openRoles: string;
    activeCandidates: string;
    avgTime: string;
    alignmentScore: string;
  };
  pipeline: { stage: string; count: string }[];
  activity_stream: string[];
}

export function useRecruiterDashboard() {
  const [state, setState] = useState<DashboardState<RecruiterDashboardData>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;
    const fetchDashboard = async () => {
      try {
        const url = API.recruiter.dashboard;
        const data = await authFetch<RecruiterDashboardData>(url);
        if (mounted) setState({ data, loading: false, error: null });
      } catch (err) {
        if (mounted) setState({ data: null, loading: false, error: (err as Error).message });
      }
    };
    fetchDashboard();
    return () => { mounted = false; };
  }, []);

  return state;
}

// Admin Dashboard Hook
export function useAdminDashboard() {
  const [state, setState] = useState<DashboardState<any>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;
    const fetchDashboard = async () => {
      try {
        const url = API.admin.dashboard;
        const data = await authFetch<any>(url);
        if (mounted) setState({ data, loading: false, error: null });
      } catch (err) {
        if (mounted) setState({ data: null, loading: false, error: (err as Error).message });
      }
    };
    fetchDashboard();
    return () => { mounted = false; };
  }, []);

  return state;
}
