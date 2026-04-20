/* ── API Response Types — Intervux AI ── */

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  role: "candidate" | "recruiter" | "admin";
}

export interface CandidateProfileResponse {
  id: number;
  user_id: string;
  name: string;
  skills: string[];
  experience_years: number | null;
  education: string | null;
  resume_url: string | null;
  resume_score: number | null;
  interview_score: number | null;
  profile_score: number | null;
  github_url: string | null;
  linkedin_url: string | null;
  mock_interviews_remaining: number;
  created_at: string;
}

export interface CandidateDashboardData {
  profile_score: number;
  resume_score: number;
  mock_interview_score: number;
  mock_interviews_remaining: number;
  recent_activity: string[];
  checklist?: { task: string; done: boolean }[];
}

export interface RecruiterDashboardData {
  stats: {
    openRoles: string;
    activeCandidates: string;
    avgTime: string;
    alignmentScore: string;
  };
  pipeline: { stage: string; count: number }[];
  candidates: {
    id: string;
    name: string;
    role: string;
    status: string;
    score?: number;
  }[];
  activity_stream: string[];
}

export interface AdminDashboardData {
  accuracy: number;
  latency_ms: number;
  token_usage: number;
  active_users: number;
  model_performance: {
    model: string;
    score: number;
  }[];
}

export interface ResumeUploadResponse {
  resume_url: string;
  resume_score: number;
  skills: string[];
  strengths: string[];
  weaknesses: string[];
}
