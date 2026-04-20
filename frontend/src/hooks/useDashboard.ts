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
  checklist: { task: string; done: boolean }[];
  nextInterviewTime: string;
  readinessScore: number;
  confidence: number;
  recommendations: string[];
  recruiterNotes: string[];
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
        // Fallback default API if api.ts isn't fully defined yet
        const url = "/api/candidate/dashboard";
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
  candidates: CandidateSummary[];
  stats: {
    openRoles: number;
    activeCandidates: number;
    avgTime: string;
    alignmentScore: string;
  };
  pipeline: { stage: string; count: number }[];
  activityStream: string[];
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
        const url = "/api/recruiter/dashboard";
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
        const url = "/api/admin/dashboard";
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
