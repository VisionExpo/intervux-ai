import { useEffect, useState } from "react";
import { authFetch, useAuth } from "../hooks/useAuth";

interface DashboardData {
  profile_score: number;
  resume_score: number;
  mock_interview_score: number;
  mock_interviews_remaining: number;
  recent_activity: string[];
}

interface ProfileData {
  name: string;
  resume_url: string | null;
}

export default function CandidateDashboard() {
  const { user } = useAuth();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [dashboardData, profileData] = await Promise.all([
          authFetch<DashboardData>("/api/candidate/dashboard"),
          authFetch<ProfileData>("/api/candidate/profile"),
        ]);
        setDashboard(dashboardData);
        setProfile(profileData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <h1>Welcome {profile?.name || user?.name || "Candidate"}</h1>
        <div className="nav-links">
          <a href="/profile">Profile</a>
          <a href="/mock-interview">Mock Interview</a>
          <a href="/interview-history">History</a>
          <a href="/notifications">Notifications</a>
        </div>
      </div>

      <div className="dashboard-status-cards">
        <div className="status-card">
          <h3>Resume uploaded</h3>
          <div className="status-indicator">
            {profile?.resume_url ? (
              <span className="status-yes">✔</span>
            ) : (
              <span className="status-no">✗</span>
            )}
          </div>
          {!profile?.resume_url && (
            <a href="/profile" className="upload-hint">Upload your resume</a>
          )}
        </div>
        
        <div className="status-card highlight">
          <h3>Mock interviews remaining</h3>
          <div className="status-value">{dashboard?.mock_interviews_remaining || 0}</div>
        </div>
      </div>

      <div className="dashboard-cards">
        <div className="score-card">
          <h3>Profile Score</h3>
          <div className="score-value">{dashboard?.profile_score.toFixed(0) || 0}</div>
        </div>
        
        <div className="score-card">
          <h3>Resume Score</h3>
          <div className="score-value">{dashboard?.resume_score.toFixed(0) || 0}</div>
        </div>
        
        <div className="score-card">
          <h3>Mock Interview Score</h3>
          <div className="score-value">{dashboard?.mock_interview_score.toFixed(0) || 0}</div>
        </div>
      </div>

      <div className="dashboard-section">
        <h2>Recent Activity</h2>
        {dashboard?.recent_activity && dashboard.recent_activity.length > 0 ? (
          <ul className="activity-list">
            {dashboard.recent_activity.map((activity, index) => (
              <li key={index}>{activity}</li>
            ))}
          </ul>
        ) : (
          <p className="no-activity">No recent activity. Start by uploading your resume or completing a mock interview.</p>
        )}
      </div>

      <div className="dashboard-actions">
        {dashboard?.mock_interviews_remaining !== undefined && dashboard.mock_interviews_remaining > 0 ? (
          <a href="/mock-interview" className="action-button primary">
            Start Mock Interview
          </a>
        ) : (
          <div className="limit-message">
            You have completed your free mock interviews.
          </div>
        )}
        <a href="/profile" className="action-button">
          Update Profile
        </a>
      </div>
    </div>
  );
}

