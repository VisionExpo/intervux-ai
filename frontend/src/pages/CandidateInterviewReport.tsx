import { useEffect, useState } from "react";

interface InterviewReport {
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

interface ReportData {
  interview: InterviewReport;
  strengths: string[];
  weaknesses: string[];
}

export default function CandidateInterviewReport() {
  const [report, setReport] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLatestReport = async () => {
      try {
        // Get the most recent completed interview
        const response = await fetch("http://localhost:8000/api/candidate/mock-interview/history", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch interview history");
        }

        const interviews: InterviewReport[] = await response.json();
        
        // Find the most recent completed interview
        const completedInterview = interviews.find(i => i.status === "completed" && i.score !== null);

        if (!completedInterview) {
          setError("No completed interview report found");
          setIsLoading(false);
          return;
        }

        // Generate sample strengths and weaknesses based on scores
        const strengths: string[] = [];
        const weaknesses: string[] = [];

        if (completedInterview.technical_score && completedInterview.technical_score >= 75) {
          strengths.push("Strong technical knowledge");
        } else if (completedInterview.technical_score && completedInterview.technical_score < 60) {
          weaknesses.push("Technical skills need improvement");
        }

        if (completedInterview.communication_score && completedInterview.communication_score >= 75) {
          strengths.push("Excellent communication");
        } else if (completedInterview.communication_score && completedInterview.communication_score < 60) {
          weaknesses.push("Communication can be improved");
        }

        if (completedInterview.reasoning_score && completedInterview.reasoning_score >= 75) {
          strengths.push("Strong problem-solving");
        } else if (completedInterview.reasoning_score && completedInterview.reasoning_score < 60) {
          weaknesses.push("Problem-solving needs work");
        }

        // Add some sample skills based on typical interview
        if (completedInterview.technical_score && completedInterview.technical_score >= 70) {
          strengths.push("Python");
        }
        if (completedInterview.technical_score && completedInterview.technical_score >= 65) {
          strengths.push("API design");
        }

        if (completedInterview.technical_score && completedInterview.technical_score < 70) {
          weaknesses.push("System design");
        }
        if (completedInterview.reasoning_score && completedInterview.reasoning_score < 70) {
          weaknesses.push("Concurrency concepts");
        }

        setReport({
          interview: completedInterview,
          strengths: strengths.length > 0 ? strengths : ["Good attempt"],
          weaknesses: weaknesses.length > 0 ? weaknesses : ["Keep practicing"],
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLatestReport();
  }, []);

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="loading">Loading report...</div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="page-container">
        <div className="report-header">
          <h1>Interview Report</h1>
          <div className="nav-links">
            <a href="/dashboard">Dashboard</a>
            <a href="/interview-history">History</a>
          </div>
        </div>
        <div className="report-content">
          <div className="error-message">{error || "No report available"}</div>
          <a href="/dashboard" className="action-button primary">
            Back to Dashboard
          </a>
        </div>
      </div>
    );
  }

  const { interview, strengths, weaknesses } = report;

  return (
    <div className="page-container">
      <div className="report-header">
        <h1>Interview Completed</h1>
        <div className="nav-links">
          <a href="/dashboard">Dashboard</a>
          <a href="/interview-history">History</a>
        </div>
      </div>

      <div className="report-content">
        <div className="report-title">
          <h2>Mock Interview #{interview.interview_number}</h2>
          <p>{interview.completed_at ? new Date(interview.completed_at).toLocaleDateString() : new Date(interview.created_at).toLocaleDateString()}</p>
        </div>

        {interview.score !== null && (
          <>
            <div className="overall-score-card">
              <span className="score-label">Score</span>
              <span className="score-value">{interview.score.toFixed(0)}</span>
            </div>

            <div className="score-breakdown">
              <h3>Score Breakdown</h3>
              <div className="score-grid">
                <div className="score-item">
                  <span className="score-label">Technical</span>
                  <span className="score-number">{interview.technical_score?.toFixed(0) || "N/A"}</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${interview.technical_score || 0}%` }}
                    ></div>
                  </div>
                </div>
                <div className="score-item">
                  <span className="score-label">Communication</span>
                  <span className="score-number">{interview.communication_score?.toFixed(0) || "N/A"}</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${interview.communication_score || 0}%` }}
                    ></div>
                  </div>
                </div>
                <div className="score-item">
                  <span className="score-label">Reasoning</span>
                  <span className="score-number">{interview.reasoning_score?.toFixed(0) || "N/A"}</span>
                  <div className="score-bar">
                    <div 
                      className="score-fill" 
                      style={{ width: `${interview.reasoning_score || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="feedback-section">
              <div className="feedback-column">
                <h3>Strengths</h3>
                <ul className="feedback-list">
                  {strengths.map((strength, index) => (
                    <li key={index} className="strength-item">
                      <span className="feedback-icon">✓</span>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="feedback-column">
                <h3>Improvements</h3>
                <ul className="feedback-list">
                  {weaknesses.map((weakness, index) => (
                    <li key={index} className="weakness-item">
                      <span className="feedback-icon">→</span>
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )}

        <div className="report-actions">
          <a href="/mock-interview" className="action-button primary">
            Start New Interview
          </a>
          <a href="/dashboard" className="action-button">
            Back to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}

