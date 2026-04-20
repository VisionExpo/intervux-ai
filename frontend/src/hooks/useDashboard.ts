import { useEffect, useState } from "react";
import { authFetch } from "./authFetch";
import { API } from "../config/api";
import type { 
  CandidateDashboardData, 
  RecruiterDashboardData, 
  AdminDashboardData 
} from "../types/api";

type DashboardState<T> = {
  data: T | null;
  loading: boolean;
  error: string | null;
};

// Candidate Dashboard Hook
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
  const [state, setState] = useState<DashboardState<AdminDashboardData>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let mounted = true;
    const fetchDashboard = async () => {
      try {
        const url = API.admin.dashboard;
        const data = await authFetch<AdminDashboardData>(url);
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
