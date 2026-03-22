import { useEffect, useState } from "react";
import { authFetch } from "../hooks/useAuth";

interface DashboardData {
  mock_interviews_remaining: number;
}

interface InterviewHistory {
  id: number;
  session_id: string;
  score: number | null;
  technical_score: number | null;
  communication_score: number | null;
  reasoning_score: number | null;
  status: string;
  interview_number: number;
  created_at: string;
  completed_at: string | null;
}

export default function MockInterview() {
  const [interviewHistory, setInterviewHistory] = useState<InterviewHistory[]>([]);
  const [interviewsRemaining, setInterviewsRemaining] = useState(3);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [dashboardData, historyData] = await Promise.all([
        authFetch<DashboardData>("/api/candidate/dashboard"),
        authFetch<InterviewHistory[]>("/api/candidate/mock-interview/history"),
      ]);
      setInterviewsRemaining(dashboardData.mock_interviews_remaining);
      setInterviewHistory(historyData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setIsLoading(false);
    }
  };

  const startInterview = async () => {
    setIsStarting(true);
    setError("");

    try {
      const response = await authFetch<{
        session_id: string;
        mock_interview_id: number;
        message: string;
      }>("/api/candidate/mock-interview/start", { method: "POST" });

      // ---------------------------------------------------------------
      // Store the session_id in sessionStorage so that useInterview can
      // append it to the WebSocket URL as ?mock_session_id=...
      // The backend gateway will link the WebSocket session to this
      // MockInterview row and write scores back on completion.
      // ---------------------------------------------------------------
      sessionStorage.setItem("mock_session_id", response.session_id);

      window.location.hash = `#/interview-session?mock_session_id=${encodeURIComponent(response.session_id)}`;
    } catch (err) {
      console.error("Failed to start interview:", err);
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setIsStarting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  const canStartInterview = interviewsRemaining > 0 && !isStarting;

  return (
    <div className="page-container">
      <div className="interview-header">
        <h1>Mock Interviews</h1>
        <div className="nav-links">
          <a href="#/dashboard">Dashboard</a>
          <a href="#/profile">Profile</a>
          <a href="#/interview-history">History</a>
          <a href="#/notifications">Notifications</a>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="interview-start-section">
        <h2>Start Your Practice Interview</h2>
        <p>
          Practice with our AI-powered mock interviewer. You'll get 3 free
          interviews to improve your skills.
        </p>

        {interviewsRemaining > 0 ? (
          <>
            <p className="interviews-remaining">
              You have <strong>{interviewsRemaining}</strong> mock interview
              {interviewsRemaining !== 1 ? "s" : ""} remaining.
            </p>
            <button
              onClick={startInterview}
              disabled={!canStartInterview}
              className="start-interview-button"
            >
              {isStarting ? "Starting..." : "Start Mock Interview"}
            </button>
          </>
        ) : (
          <div className="limit-reached">
            <p>You have completed your free mock interviews.</p>
            <p className="upgrade-hint">Upgrade to get more practice interviews.</p>
          </div>
        )}
      </div>

      <div className="interview-history-section">
        <h2>Your Interview History</h2>

        {interviewHistory.length === 0 ? (
          <p className="no-history">
            You haven't taken any mock interviews yet.
          </p>
        ) : (
          <div className="interview-list">
            {interviewHistory.map((interview) => (
              <div key={interview.id} className="interview-card">
                <div className="interview-info">
                  <h3>Mock Interview #{interview.interview_number}</h3>
                  <p className="interview-date">
                    {new Date(interview.created_at).toLocaleDateString()}
                  </p>
                  <p className="interview-status">
                    Status:{" "}
                    <span className={`status-${interview.status}`}>
                      {interview.status}
                    </span>
                  </p>
                </div>

                {interview.score !== null ? (
                  <div className="interview-scores">
                    <div className="score-item">
                      <span className="score-label">Overall</span>
                      <span className="score-value">
                        {interview.score.toFixed(0)}
                      </span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Technical</span>
                      <span className="score-value">
                        {interview.technical_score?.toFixed(0) ?? "N/A"}
                      </span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Communication</span>
                      <span className="score-value">
                        {interview.communication_score?.toFixed(0) ?? "N/A"}
                      </span>
                    </div>
                    <div className="score-item">
                      <span className="score-label">Reasoning</span>
                      <span className="score-value">
                        {interview.reasoning_score?.toFixed(0) ?? "N/A"}
                      </span>
                    </div>
                  </div>
                ) : interview.status === "in_progress" ? (
                  <div className="interview-pending">
                    <p>Interview in progress...</p>
                    <a href="#/interview-session" className="resume-button">
                      Resume Interview
                    </a>
                  </div>
                ) : (
                  <div className="interview-pending">
                    <p>Interview not completed</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
