import { useEffect, useState } from "react";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Button } from "../components/ui/Button/Button";
import { Play, Video, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import styles from "./MockInterview.module.css";
import { CreditUpgradeModal } from "../components/ui/CreditUpgradeModal";

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
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);

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
      <div className={styles.loadingState}>
        <GlassCard padding="lg">
          <div className={styles.loadingRow}>
            <div className={styles.spinner} />
            <p className={styles.loadingText}>Loading mock interviews...</p>
          </div>
        </GlassCard>
      </div>
    );
  }

  const canStartInterview = interviewsRemaining > 0 && !isStarting;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Mock Interviews</h1>
        <p className={styles.subtitle}>Practice with our AI interviewer to perfect your delivery.</p>
      </div>

      {error && (
        <GlassCard className={styles.errorCard}>
          <p className={styles.errorText}><AlertCircle size={18}/> {error}</p>
        </GlassCard>
      )}

      <div className={styles.grid}>
        {/* Left Column: Start New Interview */}
        <div className={styles.startColumn}>
          <GlassCard padding="lg" className={styles.startCard}>
            <div className={styles.startCardOverlay} />
            <h2 className={styles.startHeading}>
              <Video /> Start Practice
            </h2>
            <p className={styles.startDescription}>
              Practice with our AI-powered mock interviewer. You get 3 free interviews to improve your skills.
            </p>

            {interviewsRemaining > 0 ? (
              <div className={styles.startContent}>
                <div className={styles.remainingBox}>
                  <p className={styles.remainingLabel}>Interviews Remaining</p>
                  <p className={styles.remainingValue}>{interviewsRemaining}</p>
                </div>
                <Button
                  onClick={startInterview}
                  disabled={!canStartInterview}
                  fullWidth
                >
                  {isStarting ? "Starting..." : <><Play size={16} /> Start Interview</>}
                </Button>
              </div>
            ) : (
              <div className={styles.limitBox}>
                <p className={styles.limitTitle}>Limit Reached</p>
                <p className={styles.limitText}>You have completed your free mock interviews.</p>
                <Button variant="secondary" fullWidth onClick={() => setIsUpgradeModalOpen(true)}>Upgrade Plan</Button>
              </div>
            )}
          </GlassCard>
        </div>

        <CreditUpgradeModal isOpen={isUpgradeModalOpen} onClose={() => setIsUpgradeModalOpen(false)} />

        {/* Right Column: History */}
        <div className={styles.historyColumn}>
          <h2 className={styles.historyTitle}>Recent Sessions</h2>

          {interviewHistory.length === 0 ? (
            <GlassCard className={styles.emptyState}>
              <Clock className={styles.emptyIcon} size={48} />
              <p className={styles.emptyText}>You haven't taken any mock interviews yet.</p>
            </GlassCard>
          ) : (
            <div className={styles.historyCards}>
              {interviewHistory.map((interview) => (
                <GlassCard key={interview.id} className={styles.historyCard}>
                  <div className={styles.historyCardContent}>
                    <div>
                      <h3 className={styles.sessionTitle}>
                        Session #{interview.interview_number}
                        {interview.status === "completed" && <CheckCircle2 size={16} />}
                      </h3>
                      <p className={styles.sessionDate}>
                        {new Date(interview.created_at).toLocaleDateString(undefined, {
                          year: 'numeric', month: 'long', day: 'numeric',
                          hour: '2-digit', minute: '2-digit'
                        })}
                      </p>
                    </div>

                    {interview.score !== null ? (
                      <div className={styles.scoresRow}>
                        <div className={styles.scoreItem}>
                          <p className={styles.scoreLabel}>Overall</p>
                          <p className={styles.scoreValuePrimary}>{interview.score.toFixed(0)}</p>
                        </div>
                        <div className={styles.scoreItem}>
                          <p className={styles.scoreLabel}>Tech</p>
                          <p className={styles.scoreValueSecondary}>{interview.technical_score?.toFixed(0) ?? "-"}</p>
                        </div>
                        <div className={styles.scoreItem}>
                          <p className={styles.scoreLabel}>Comm</p>
                          <p className={styles.scoreValueSecondary}>{interview.communication_score?.toFixed(0) ?? "-"}</p>
                        </div>
                      </div>
                    ) : interview.status === "in_progress" ? (
                      <div>
                        <Button variant="secondary" onClick={() => window.location.hash = `#/interview-session?mock_session_id=${encodeURIComponent(interview.session_id)}`}>
                          Resume Pending
                        </Button>
                      </div>
                    ) : (
                      <div>
                        <span className={styles.incompleteBadge}>Incomplete</span>
                      </div>
                    )}
                  </div>
                </GlassCard>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
