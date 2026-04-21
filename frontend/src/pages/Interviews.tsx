import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { authFetch } from "../hooks/authFetch";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import { Button } from "../components/ui/Button/Button";
import { 
  Users, 
  Mic2, 
  Calendar, 
  ChevronRight, 
  History, 
  AlertCircle,
  FileText,
  Sparkles
} from "lucide-react";
import { CreditUpgradeModal } from "../components/ui/CreditUpgradeModal";
import styles from "./Interviews.module.css";

interface InterviewRecord {
  id: number;
  session_id: string;
  score: number | null;
  status: string;
  interview_number: number;
  created_at: string;
  type?: "practice" | "invited";
}

interface ProfileData {
  mock_interviews_remaining: number;
  resume_url: string | null;
}

export default function Interviews() {
  const navigate = useNavigate();
  const [interviews, setInterviews] = useState<InterviewRecord[]>([]);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isUpgradeModalOpen, setIsUpgradeModalOpen] = useState(false);
  const [error, setError] = useState("");
  const startSectionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    Promise.all([
      authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history"),
      authFetch<ProfileData>("/api/candidate/profile")
    ])
      .then(([history, profileData]) => {
        setInterviews(history);
        setProfile(profileData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load data"))
      .finally(() => setIsLoading(false));
  }, []);

  const startInterview = async () => {
    if (isStarting) return;
    setIsStarting(true);
    setError("");

    try {
      const response = await authFetch<{
        session_id: string;
        mock_interview_id: number;
        message: string;
      }>("/api/candidate/mock-interview/start", { method: "POST" });

      sessionStorage.setItem("mock_session_id", response.session_id);
      // Fresh navigation with session ID in query
      navigate(`/interview-session?mock_session_id=${encodeURIComponent(response.session_id)}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start interview");
    } finally {
      setIsStarting(false);
    }
  };

  const scrollToStart = () => {
    const el = document.getElementById("start-practice");
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  const getResumeFilename = (url: string | null) => {
    if (!url) return "No resume uploaded";
    const filename = url.split("/").pop();
    return filename || "No resume uploaded";
  };

  const getStatusLabel = (status: string) => {
    const statusMap: Record<string, string> = {
      completed: "Completed",
      in_progress: "In Progress",
      abandoned: "Failed",
    };
    return statusMap[status] || (status ? status.replace("_", " ") : "Unknown");
  };

  const getStatusClass = (status: string) => {
    if (status === "completed") return styles.statusCompleted;
    if (status === "in_progress") return styles.statusInProgress;
    return styles.statusFailed;
  };

  // Start Button State awareness logic
  const hasResume = !!profile?.resume_url;
  const credits = profile?.mock_interviews_remaining ?? 0;
  const hasCredits = credits > 0;

  // Priority ordered evaluation for labels and actions
  let buttonText = isStarting ? "Starting..." : "Start Interview";
  let buttonAction = startInterview;
  let variant: "primary" | "secondary" = "primary";

  if (!hasResume) {
    buttonText = "Upload resume to start";
    buttonAction = () => navigate("/profile");
    variant = "secondary";
  } else if (!hasCredits) {
    buttonText = "No credits remaining";
    buttonAction = () => {
      if (isUpgradeModalOpen) return;
      setIsUpgradeModalOpen(true);
    };
    variant = "secondary";
  }

  if (isLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.emptyState}>
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          <p>Loading your interviews...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>
          <Mic2 size={32} /> Interviews
        </h1>
        <p className={styles.subtitle}>Practice, track, and manage your interview sessions</p>
      </header>

      {/* 1. START PRACTICE */}
      <section className={styles.section} ref={startSectionRef} id="start-practice">
        <h2 className={styles.sectionTitle}><Sparkles size={20} color="var(--accent-primary)" /> Start Practice</h2>
        <GlassCard className={styles.practiceCard} padding="lg">
          <div className={styles.practiceLayout}>
            <div className={styles.practiceInfo}>
              <h3 className={styles.practiceTitle}>AI Mock Interview</h3>
              <p className={styles.practiceDesc}>
                Experience a high-fidelity AI interview tailored to your profile. 
                Get instant feedback, scores, and a detailed performance report.
              </p>
              
              <div className={styles.practiceMeta}>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Remaining</span>
                  <span className={styles.metaValue}>
                    {credits} {credits === 1 ? 'Interview' : 'Interviews'} Remaining
                  </span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>Resume</span>
                  <span className={styles.metaValue}>
                    {hasResume ? (
                      <>
                        <FileText size={16} /> 
                        {getResumeFilename(profile.resume_url)}
                        <button className={styles.resumeLink} onClick={() => navigate("/profile")}>[Change]</button>
                      </>
                    ) : (
                      <span style={{ color: 'var(--error)' }}><AlertCircle size={14} /> None uploaded</span>
                    )}
                  </span>
                </div>
              </div>
            </div>

            <div className={styles.practiceAction}>
              <Button 
                onClick={buttonAction} 
                className={styles.startButton}
                variant={variant}
                disabled={isStarting}
              >
                {buttonText}
              </Button>
            </div>
          </div>
        </GlassCard>
      </section>

      <CreditUpgradeModal 
        isOpen={isUpgradeModalOpen} 
        onClose={() => setIsUpgradeModalOpen(false)} 
      />

      {/* 2. UPCOMING INTERVIEWS */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}><Calendar size={20} /> Upcoming Interviews</h2>
        <GlassCard className={styles.upcomingCard}>
          <div className={styles.emptyState}>
            <Calendar className={styles.emptyIcon} size={40} />
            <p className={styles.emptyText}>
              No upcoming interviews yet. <br/> Recruiters will invite you here.
            </p>
          </div>
        </GlassCard>
      </section>

      {/* 3. RECENT SESSIONS */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}><History size={20} /> Recent Sessions</h2>
        <GlassCard padding="none">
          {interviews.length === 0 ? (
            <div className={styles.emptyState}>
              <History className={styles.emptyIcon} size={40} />
              <p className={styles.emptyText}>
                No interviews yet — start your first AI-powered interview and get instant feedback
              </p>
              <Button onClick={scrollToStart} variant="secondary" outline>
                Start Interview
              </Button>
            </div>
          ) : (
            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th className={styles.th}>Session</th>
                    <th className={styles.th}>Date</th>
                    <th className={styles.th}>Type</th>
                    <th className={styles.th}>Status</th>
                    <th className={styles.th}>Score</th>
                    <th className={styles.th}></th>
                  </tr>
                </thead>
                <tbody>
                  {interviews.map((item) => (
                    <tr key={item.id} className={styles.tr}>
                      <td className={styles.td}>#{item.interview_number}</td>
                      <td className={styles.td}>{new Date(item.created_at).toLocaleDateString()}</td>
                      <td className={styles.td}>
                        <span className={`${styles.badge} ${item.type === 'invited' ? styles.badgeInvited : styles.badgePractice}`}>
                          {item.type === 'invited' ? 'Invited' : 'Practice'}
                        </span>
                      </td>
                      <td className={`${styles.td} ${getStatusClass(item.status)}`}>
                        {getStatusLabel(item.status)}
                      </td>
                      <td className={styles.td}>
                        <span className={styles.scoreValue}>
                          {item.score !== null ? `${item.score.toFixed(0)}%` : "-"}
                        </span>
                      </td>
                      <td className={styles.td}>
                        {item.status === 'completed' && (
                          <button 
                            className={styles.actionBtn} 
                            onClick={() => navigate(`/report/${item.session_id}`)}
                          >
                            View Report <ChevronRight size={14} style={{ display: 'inline' }} />
                          </button>
                        )}
                        {item.status === 'abandoned' && (
                          <button 
                            className={styles.actionBtn} 
                            onClick={scrollToStart}
                            style={{ color: 'var(--accent-primary)' }}
                          >
                            Retry (No Deduction)
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </GlassCard>
      </section>
    </div>
  );
}
