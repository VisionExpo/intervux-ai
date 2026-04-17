import { useEffect, useState } from "react";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Button } from "../components/ui/Button/Button";
import { History, X, ChevronRight, BarChart3 } from "lucide-react";
import styles from "./InterviewHistory.module.css";

interface InterviewRecord {
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

interface SelectedDetail {
  interview: InterviewRecord;
}

function ScoreBar({ label, value }: { label: string; value: number | null }) {
  const pct = value ?? 0;
  return (
    <div className={styles.scoreBarWrap}>
      <div className={styles.scoreBarHeader}>
        <span className={styles.scoreBarLabel}>{label}</span>
        <span className={styles.scoreBarValue}>{value !== null ? value.toFixed(0) : "-"}</span>
      </div>
      <div className={styles.scoreBarTrack}>
        <div className={styles.scoreBarFill} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const isCompleted = status === "completed";
  return (
    <span className={`${styles.statusBadge} ${isCompleted ? styles.statusCompleted : styles.statusOther}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function InterviewHistory() {
  const [interviews, setInterviews] = useState<InterviewRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<SelectedDetail | null>(null);

  useEffect(() => {
    authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history")
      .then(setInterviews)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load history"))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className={styles.loadingState}>
        <GlassCard padding="lg">
          <div className={styles.loadingRow}>
            <div className={styles.spinner} />
            <p className={styles.loadingText}>Loading interview history...</p>
          </div>
        </GlassCard>
      </div>
    );
  }

  const completed = interviews.filter((i) => i.status === "completed" && i.score !== null);
  const avgScore =
    completed.length > 0
      ? completed.reduce((sum, i) => sum + (i.score ?? 0), 0) / completed.length
      : null;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>
          <History /> Interview History
        </h1>
        <p className={styles.subtitle}>Review your past performance and mock interview results.</p>
      </div>

      {error && (
        <GlassCard className={styles.errorCard}>
          <p className={styles.errorText}>{error}</p>
        </GlassCard>
      )}

      {/* Summary cards */}
      <div className={styles.summaryGrid}>
        <GlassCard className={styles.summaryCard}>
          <div className={`${styles.summaryOverlay} ${styles.summaryOverlayBlue}`} />
          <h3 className={styles.summaryLabel}>Total Sessions</h3>
          <p className={styles.summaryValue}>{interviews.length}</p>
        </GlassCard>
        <GlassCard className={styles.summaryCard}>
          <div className={`${styles.summaryOverlay} ${styles.summaryOverlayGreen}`} />
          <h3 className={styles.summaryLabel}>Completed</h3>
          <p className={styles.summaryValue}>{completed.length}</p>
        </GlassCard>
        <GlassCard className={`${styles.summaryCard} ${styles.summaryBorderAccent}`}>
          <div className={`${styles.summaryOverlay} ${styles.summaryOverlayIndigo}`} />
          <h3 className={`${styles.summaryLabel} ${styles.summaryLabelWide}`}>Average Score</h3>
          <p className={styles.summaryValueAccent}>
            {avgScore !== null ? avgScore.toFixed(0) : "-"}
          </p>
        </GlassCard>
      </div>

      <GlassCard padding="none" style={{ overflow: "hidden" }}>
        <div className={styles.tableHeader}>
          <h2 className={styles.tableTitle}>All Sessions</h2>
        </div>

        {interviews.length === 0 ? (
          <div className={styles.emptyState}>
            <BarChart3 className={styles.emptyIcon} size={48} />
            <p className={styles.emptyText}>No mock interviews yet.</p>
            <Button onClick={() => window.location.hash = "#/mock-interview"}>
              Start your first interview
            </Button>
          </div>
        ) : (
          <div className={styles.tableWrap}>
            <table className={styles.table}>
              <thead className={styles.tableHead}>
                <tr>
                  <th>Session</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th className={styles.thCenter}>Overall</th>
                  <th className={`${styles.thCenter} ${styles.thHiddenMd}`}>Technical</th>
                  <th className={`${styles.thCenter} ${styles.thHiddenMd}`}>Comm</th>
                  <th className={`${styles.thCenter} ${styles.thHiddenLg}`}>Reasoning</th>
                  <th></th>
                </tr>
              </thead>
              <tbody className={styles.tableBody}>
                {interviews.map((interview) => (
                  <tr
                    key={interview.id}
                    className={`${styles.tableRow} ${selected?.interview.id === interview.id ? styles.tableRowSelected : ""}`}
                    onClick={() =>
                      setSelected(
                        selected?.interview.id === interview.id
                          ? null
                          : { interview }
                      )
                    }
                  >
                    <td className={`${styles.td} ${styles.tdSession}`}>
                      #{interview.interview_number}
                    </td>
                    <td className={`${styles.td} ${styles.tdDate}`}>
                      {new Date(interview.created_at).toLocaleDateString()}
                    </td>
                    <td className={styles.td}>
                      <StatusBadge status={interview.status} />
                    </td>
                    <td className={`${styles.td} ${styles.tdScore}`}>
                      {interview.score !== null ? interview.score.toFixed(0) : "-"}
                    </td>
                    <td className={`${styles.td} ${styles.tdSecondary} ${styles.tdHiddenMd}`}>
                      {interview.technical_score !== null ? interview.technical_score.toFixed(0) : "-"}
                    </td>
                    <td className={`${styles.td} ${styles.tdSecondary} ${styles.tdHiddenMd}`}>
                      {interview.communication_score !== null ? interview.communication_score.toFixed(0) : "-"}
                    </td>
                    <td className={`${styles.td} ${styles.tdSecondary} ${styles.tdHiddenLg}`}>
                      {interview.reasoning_score !== null ? interview.reasoning_score.toFixed(0) : "-"}
                    </td>
                    <td className={`${styles.td} ${styles.tdAction}`}>
                      {interview.status === "completed" ? (
                        <div className={styles.viewLink}>
                          View <ChevronRight size={14} />
                        </div>
                      ) : ""}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {/* Detail Modal */}
      {selected && (
        <div className={styles.modalBackdrop} onClick={() => setSelected(null)}>
          <div className={styles.modalPanel} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h3 className={styles.modalTitle}>Mock Interview #{selected.interview.interview_number}</h3>
              <button onClick={() => setSelected(null)} className={styles.modalClose}>
                <X size={20} />
              </button>
            </div>

            <div className={styles.modalDetails}>
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Date</span>
                <span className={styles.detailValue}>{new Date(selected.interview.created_at).toLocaleString()}</span>
              </div>
              {selected.interview.completed_at && (
                <div className={styles.detailRow}>
                  <span className={styles.detailLabel}>Completed</span>
                  <span className={styles.detailValue}>{new Date(selected.interview.completed_at).toLocaleString()}</span>
                </div>
              )}
              <div className={styles.detailRow}>
                <span className={styles.detailLabel}>Status</span>
                <StatusBadge status={selected.interview.status} />
              </div>
            </div>

            {selected.interview.score !== null && (
              <div className={styles.modalScores}>
                <h4 className={styles.modalScoresTitle}>Score Breakdown</h4>
                <div className={styles.modalScoresGrid}>
                  <ScoreBar label="Overall" value={selected.interview.score} />
                  <ScoreBar label="Technical" value={selected.interview.technical_score} />
                  <ScoreBar label="Communication" value={selected.interview.communication_score} />
                  <ScoreBar label="Reasoning" value={selected.interview.reasoning_score} />
                </div>
              </div>
            )}

            <div className={styles.modalActions}>
              {selected.interview.status === "completed" && (
                <Button onClick={() => window.location.hash = "#/report"}>
                  View Full Report
                </Button>
              )}
              <Button variant="secondary" onClick={() => setSelected(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
