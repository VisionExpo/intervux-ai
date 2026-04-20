import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Briefcase, CheckCircle2, Rocket, ShieldCheck, Sparkles } from "lucide-react";
import { authFetch } from "../hooks/authFetch";
import { SurfaceCard } from "../components/ui/SurfaceCard";

interface InviteData {
  candidate: {
    name: string;
    role: string;
  };
  job: {
    title: string;
    description: string;
  } | null;
  status: string;
}

export default function InviteLandingPage() {
  const { token } = useParams<{ token: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<InviteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function validate() {
      try {
        const response = await authFetch(`${import.meta.env.VITE_API_URL}/api/candidate/invite/validate/${token}`);
        if (!response.ok) throw new Error("Invalid or expired invitation token.");
        const json = await response.json();
        setData(json);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    validate();
  }, [token]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center p-6 text-[var(--text-primary)]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-[var(--accent-ocean)] border-t-transparent rounded-full animate-spin" />
          <p className="animate-pulse">Validating Secure Invitation...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#0a0a0c] flex items-center justify-center p-6">
        <SurfaceCard className="max-w-md w-full text-center p-12 border-rose-500/30">
          <div className="inline-flex p-4 rounded-full bg-rose-500/10 text-rose-500 mb-6">
            <ShieldCheck size={48} />
          </div>
          <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Invalid Invitation</h2>
          <p className="text-[var(--text-secondary)] mb-8">{error}</p>
          <button 
            onClick={() => navigate("/")}
            className="w-full py-3 bg-[var(--surface-glass-light)] border border-[var(--border-glass)] rounded-xl text-[var(--text-primary)] font-semibold transition-all hover:bg-white/10"
          >
            Return Home
          </button>
        </SurfaceCard>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0a0a0c] relative overflow-hidden flex items-center justify-center p-6">
      {/* Background Decor */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[var(--accent-ocean)] opacity-10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-[var(--accent-indigo)] opacity-10 blur-[120px] rounded-full pointer-events-none" />

      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full"
      >
        <SurfaceCard className="relative p-10 overflow-hidden border-[var(--border-glass)] glass-heavy shadow-2xl">
          <div className="absolute top-0 right-0 p-4 opacity-20">
            <Rocket size={120} />
          </div>

          <div className="relative z-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--accent-ocean-glow)] text-[var(--accent-ocean)] text-xs font-bold border border-sky-500/30 mb-6">
              <Sparkles size={14} />
              EXPIRED EXCLUSIVE INVITE
            </div>

            <h1 className="text-4xl font-bold text-[var(--text-primary)] mb-2 tracking-tight">
              Welcome, {data?.candidate.name}
            </h1>
            <p className="text-xl text-[var(--text-secondary)] mb-8">
              You've been invited to interview for <span className="text-[var(--text-primary)] font-semibold">{data?.job?.title}</span>
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10 text-left">
              <div className="bg-[var(--surface-glass-light)] p-5 rounded-2xl border border-[var(--border-glass)] shadow-inner">
                <div className="flex items-center gap-3 text-[var(--accent-ocean)] mb-3">
                  <Briefcase size={20} />
                  <span className="font-semibold text-sm">Role Details</span>
                </div>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {data?.job?.description || "High-priority engineering role focusing on AI scalability."}
                </p>
              </div>
              <div className="bg-[var(--surface-glass-light)] p-5 rounded-2xl border border-[var(--border-glass)] shadow-inner">
                <div className="flex items-center gap-3 text-[var(--accent-indigo)] mb-3">
                  <CheckCircle2 size={20} />
                  <span className="font-semibold text-sm">AI-Powered Evaluation</span>
                </div>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  Experience a modern, objective interview process with real-time AI feedback.
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-4">
              <button 
                onClick={() => navigate("/signup", { state: { inviteToken: token, email: data?.candidate.name } })}
                className="w-full py-4 bg-[var(--accent-ocean)] text-white rounded-2xl font-bold text-lg shadow-xl shadow-sky-500/20 transform transition-all hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
              >
                Accept & Start Interview
              </button>
              <p className="text-center text-xs text-[var(--text-secondary)]">
                By continuing, you agree to Intervux AI's Terms of Service and Privacy Policy.
              </p>
            </div>
          </div>
        </SurfaceCard>
      </motion.div>
    </div>
  );
}
