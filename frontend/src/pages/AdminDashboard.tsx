import { useEffect, useState } from "react";

import AIEvaluationDashboard from "../components/dashboard/AIEvaluationDashboard";
import { authFetch, useAuth } from "../hooks/useAuth";
import type { EvaluationDashboardResponse } from "../types";

export default function AdminDashboard() {
  const { logout, user } = useAuth();
  const [evaluationData, setEvaluationData] = useState<EvaluationDashboardResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const dashboardMetrics = await authFetch<EvaluationDashboardResponse>("/api/evaluation-dashboard");
        setEvaluationData(dashboardMetrics);
      } catch (requestError) {
        setError(requestError instanceof Error ? requestError.message : "Failed to load dashboard metrics");
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  if (isLoading) {
    return <main className="dashboard-shell">Loading admin dashboard...</main>;
  }

  return (
    <main className="dashboard-shell">
      <header>
        <h1>Admin Dashboard</h1>
        <div className="header-actions">
          {user && (
            <span className="user-info">
              {user.name} ({user.role})
            </span>
          )}
          <button type="button" className="logout-btn" onClick={logout}>
            Logout
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </header>

      <nav className="top-tabs">
        <button type="button" className="active">
          AI Evaluation & Metrics
        </button>
      </nav>

      <div className="dashboard-grid">
        <AIEvaluationDashboard data={evaluationData} />
      </div>
    </main>
  );
}
