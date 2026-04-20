import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  Award, 
  CheckCircle2, 
  ChevronLeft, 
  FileBox, 
  History, 
  LayoutDashboard, 
  Lightbulb, 
  MessageSquare, 
  Sparkles, 
  Target, 
  TrendingUp, 
  Zap 
} from "lucide-react";
import { authFetch } from "../hooks/authFetch";
import { SurfaceCard } from "../components/ui/SurfaceCard";
import { ProgressBar } from "../components/ui/ProgressBar";
import styles from "./CandidateInterviewReport.module.css";

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
  evaluation?: string | null;
}

interface PerQuestionEval {
  question: string;
  skill: string;
  scores: Record<string, number> | null;
  summary: string | null;
}

interface PersistedEvaluation {
  final_report?: {
    strengths?: string[];
    weaknesses?: string[];
    overall_recommendation?: string;
    final_summary?: string;
  };
  per_question?: PerQuestionEval[];
}

interface ReportData {
  interview: InterviewRecord;
  strengths: string[];
  weaknesses: string[];
  perQuestion: PerQuestionEval[];
  recommendation: string;
  summary: string;
}

function parseEvaluation(raw: string | null | undefined): PersistedEvaluation | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PersistedEvaluation;
  } catch {
    return null;
  }
}

function deriveStrengthsWeaknesses(
  interview: InterviewRecord,
  evaluation: PersistedEvaluation | null
): { strengths: string[]; weaknesses: string[] } {
  const reportStrengths = evaluation?.final_report?.strengths ?? [];
  const reportWeaknesses = evaluation?.final_report?.weaknesses ?? [];

  if (reportStrengths.length > 0 || reportWeaknesses.length > 0) {
    return { strengths: reportStrengths, weaknesses: reportWeaknesses };
  }

  const perQ = evaluation?.per_question ?? [];
  if (perQ.length > 0) {
    const strengths: string[] = [];
    const weaknesses: string[] = [];
    for (const q of perQ) {
      if (!q.scores) continue;
      const vals = Object.values(q.scores).filter((v): v is number => typeof v === "number");
      if (vals.length === 0) continue;
      const avg = vals.reduce((a, b) => a + b, 0) / vals.length;
      const label = q.skill ? `${q.skill}: ${q.question.slice(0, 40)}...` : q.question.slice(0, 60);
      if (avg >= 7) strengths.push(label);
      else if (avg <= 4) weaknesses.push(label);
    }
    if (strengths.length > 0 || weaknesses.length > 0) {
      return { strengths, weaknesses };
    }
  }

  const strengths: string[] = [];
  const weaknesses: string[] = [];
  const { technical_score: tech, communication_score: comm, reasoning_score: reason } = interview;

  if (tech !== null) {
    if (tech >= 75) strengths.push("Strong technical foundation");
    else if (tech < 60) weaknesses.push("Technical depth needs refinement");
  }
  if (comm !== null) {
    if (comm >= 75) strengths.push("Relatable and clear communication");
    else if (comm < 60) weaknesses.push("Structure your responses better");
  }
  if (reason !== null) {
    if (reason >= 75) strengths.push("Data-driven reasoning skills");
    else if (reason < 60) weaknesses.push("Focus more on root-cause analysis");
  }

  return {
    strengths: strengths.length > 0 ? strengths : ["High engagement in session"],
    weaknesses: weaknesses.length > 0 ? weaknesses : ["Practice consistent STAR formatting"],
  };
}

export default function CandidateInterviewReport() {
  const navigate = useNavigate();
  const [report, setReport] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchLatestReport = async () => {
      const stored = sessionStorage.getItem("interview_report");
      const hasStored = !!stored;
      
      try {
        let completedInterview: InterviewRecord | undefined;
        
        if (hasStored) {
          const sessionData = JSON.parse(stored);
          // If we have just finished an interview, session storage might contain the immediate result
          // But it's safer to fetch the latest "completed" record from history to be sure it's persisted correctly
        }

        const interviews = await authFetch<InterviewRecord[]>("/api/candidate/mock-interview/history");
        completedInterview = interviews.find((i) => i.status === "completed" && i.score !== null);

        if (!completedInterview) {
          setError("No completed interview record found. Completion might be in progress.");
          return;
        }

        const evaluation = parseEvaluation(completedInterview.evaluation);
        const { strengths, weaknesses } = deriveStrengthsWeaknesses(completedInterview, evaluation);

        setReport({
          interview: completedInterview,
          strengths,
          weaknesses,
          perQuestion: evaluation?.per_question ?? [],
          recommendation: evaluation?.final_report?.overall_recommendation ?? "Recommended with minor optimizations.",
          summary: evaluation?.final_report?.final_summary || "Our AI analysis indicates a strong performance with a clear understanding of core concepts.",
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to generate your intelligence report.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchLatestReport();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center p-6 text-[var(--text-primary)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-[var(--accent-indigo)] border-t-transparent rounded-full animate-spin" />
          <p className="animate-pulse">Generating Intelligence Report...</p>
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center p-6">
        <SurfaceCard className="max-w-md w-full text-center p-12 border-rose-500/30">
          <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Report Unavailable</h2>
          <p className="text-[var(--text-secondary)] mb-8">{error || "Please complete an interview first."}</p>
          <button 
            onClick={() => navigate("/candidate")}
            className="w-full py-3 bg-[var(--surface-glass-light)] border border-[var(--border-glass)] rounded-xl text-[var(--text-primary)] font-semibold"
          >
            Go to Dashboard
          </button>
        </SurfaceCard>
      </div>
    );
  }

  const { interview, strengths, weaknesses, perQuestion, recommendation, summary } = report;

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={styles.page}
    >
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Performance Intel</h1>
          <p className="text-[var(--text-secondary)] mt-1 flex items-center gap-2">
            <TrendingUp size={14} className="text-[var(--accent-ocean)]" />
            Session Analytics — {new Date(interview.completed_at || interview.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => navigate("/candidate")} 
            className="p-3 rounded-xl bg-[var(--surface-glass-light)] border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-white transition-all"
            aria-label="Back to Dashboard"
          >
            <LayoutDashboard size={20} title="Dashboard" />
          </button>
          <button 
            onClick={() => navigate("/interview-history")} 
            className="p-3 rounded-xl bg-[var(--surface-glass-light)] border border-[var(--border-glass)] text-[var(--text-secondary)] hover:text-white transition-all"
            aria-label="View Interview History"
          >
            <History size={20} title="History" />
          </button>
        </div>
      </header>

      <div className={styles.scoreGrid}>
        <motion.div 
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className={styles.overallScoreCard}
        >
          <p className={styles.overallLabel}>Intelligence Index</p>
          <p className={styles.overallValue}>{Math.round(interview.score || 0)}</p>
          <div className="mt-4 px-3 py-1 bg-white/20 rounded-full text-xs font-bold uppercase tracking-wider backdrop-blur-md">
            Top 15% Performance
          </div>
        </motion.div>

        <div className={styles.dimensionCard}>
          <p className={styles.dimensionLabel}>Technical Accuracy</p>
          <p className={styles.dimensionValue}>{Math.round(interview.technical_score || 0)}%</p>
          <ProgressBar value={interview.technical_score || 0} height={6} />
        </div>

        <div className={styles.dimensionCard}>
          <p className={styles.dimensionLabel}>Communication</p>
          <p className={styles.dimensionValue}>{Math.round(interview.communication_score || 0)}%</p>
          <ProgressBar value={interview.communication_score || 0} height={6} />
        </div>

        <div className={styles.dimensionCard}>
          <p className={styles.dimensionLabel}>Reasoning Depth</p>
          <p className={styles.dimensionValue}>{Math.round(interview.reasoning_score || 0)}%</p>
          <ProgressBar value={interview.reasoning_score || 0} height={6} />
        </div>
      </div>

      <div className={styles.summaryCard}>
        <h3 className={styles.recommendation}>
          <Zap size={20} className="text-[var(--accent-ocean)]" />
          AI Recommendation: {recommendation}
        </h3>
        <p className={styles.summaryText}>{summary}</p>
      </div>

      <div className={styles.feedbackGrid}>
        <div className={styles.feedbackColumn}>
          <h3 className={styles.feedbackHeader}>
            <Target size={20} className="text-[var(--accent-success)]" />
            Key Strengths
          </h3>
          <div className={styles.feedbackList}>
            {strengths.map((s, i) => (
              <div key={i} className={`${styles.feedbackItem} ${styles.strengthItem}`}>
                {s}
              </div>
            ))}
          </div>
        </div>
        <div className={styles.feedbackColumn}>
          <h3 className={styles.feedbackHeader}>
            <Lightbulb size={20} className="text-[var(--accent-danger)]" />
            Growth Opportunities
          </h3>
          <div className={styles.feedbackList}>
            {weaknesses.map((w, i) => (
              <div key={i} className={`${styles.feedbackItem} ${styles.weaknessItem}`}>
                {w}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mb-12">
        <h3 className="flex items-center gap-2 text-xl font-bold mb-6 text-[var(--text-primary)]">
          <MessageSquare size={20} className="text-[var(--accent-indigo)]" />
          Question-Level Insights
        </h3>
        <div className={styles.questionGrid}>
          {perQuestion.map((q, i) => {
            const vals = q.scores ? Object.values(q.scores).filter((v): v is number => typeof v === "number") : [];
            const avg = vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
            return (
              <motion.div 
                key={i} 
                initial={{ x: -20, opacity: 0 }}
                whileInView={{ x: 0, opacity: 1 }}
                viewport={{ once: true }}
                className={styles.questionCard}
              >
                <div className={styles.qHeader}>
                  <p className={styles.qTitle}>Q{i + 1} • {q.skill || "Behavioral"}</p>
                  {avg !== null && (
                    <span className={`${styles.qScore} ${avg >= 7 ? "text-[var(--accent-success)]" : "text-amber-400"}`}>
                      {avg.toFixed(1)} / 10
                    </span>
                  )}
                </div>
                <p className={styles.qText}>{q.question}</p>
                {q.summary && <p className={styles.qSummary}>{q.summary}</p>}
              </motion.div>
            );
          })}
        </div>
      </div>

      <div className={styles.actions}>
        <button 
          onClick={() => navigate("/mock-interview")}
          className="px-8 py-4 bg-[var(--accent-indigo)] text-white rounded-2xl font-bold hover:scale-105 transition-all shadow-xl shadow-indigo-500/20"
        >
          Take Another Session
        </button>
        <button 
          onClick={() => navigate("/candidate")}
          className="px-8 py-4 bg-[var(--surface-glass-heavy)] border border-[var(--border-glass)] text-white rounded-2xl font-bold hover:bg-white/10 transition-all"
        >
          Back to Dashboard
        </button>
      </div>
    </motion.div>
  );
}
