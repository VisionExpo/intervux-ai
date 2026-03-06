export type DashboardTab = "candidates" | "interviews" | "analytics";

export interface CandidateListItem {
  id: string;
  name: string;
  email: string;
  role: string;
  resume_url: string;
  created_at: string;
  interview_id?: string;
}

export interface InterviewScoreCard {
  id: string;
  candidate_id: string;
  role: string;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  problem_solving_score: number;
  started_at: string;
  completed_at: string;
}

export interface InterviewQuestion {
  id: string;
  interview_id: string;
  question: string;
  answer: string;
  score: number;
  feedback: string;
}

export interface ReplaySegment {
  question: string;
  candidate_audio: string;
  transcript: string;
  evaluation: {
    technical: number;
    clarity: number;
    reasoning: number;
  };
}

export interface CandidateInterviewReport {
  candidate: CandidateListItem;
  interview: InterviewScoreCard;
  questions: InterviewQuestion[];
  replay_segments: ReplaySegment[];
}

export interface SkillAnalyticsResponse {
  interview_id: string;
  skills: Record<string, number>;
}

export interface CandidateComparisonRow {
  candidate_id: string;
  candidate_name: string;
  technical: number;
  communication: number;
  overall: number;
}
