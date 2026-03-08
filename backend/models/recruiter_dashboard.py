from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class JobSkill(BaseModel):
    id: str
    job_post_id: str
    skill_name: str
    is_required: bool
    proficiency_level: Optional[str] = None


class JobPost(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    experience_level: str
    status: str
    ai_interview_enabled: bool
    interview_limit: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    skills: List[JobSkill] = []


class JobPostCreate(BaseModel):
    title: str
    description: Optional[str] = None
    experience_level: str = "mid"
    ai_interview_enabled: bool = False
    interview_limit: Optional[int] = None
    skills: List[str] = []  # List of skill names


class JobPostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    ai_interview_enabled: Optional[bool] = None
    interview_limit: Optional[int] = None
    skills: Optional[List[str]] = None


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    role: str
    resume_url: str
    created_at: datetime
    status: str = "invited"
    job_post_id: Optional[str] = None
    interview_link: Optional[str] = None
    interview_link_expires_at: Optional[datetime] = None


class CandidateCreate(BaseModel):
    name: str
    email: str
    role: str
    job_post_id: Optional[str] = None
    resume_url: Optional[str] = None


class InterviewSummary(BaseModel):
    id: str
    candidate_id: str
    role: str
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    started_at: datetime
    completed_at: datetime


class QuestionBreakdown(BaseModel):
    id: str
    interview_id: str
    question: str
    answer: str
    score: float
    feedback: str


class ReplayEvaluation(BaseModel):
    technical: float
    clarity: float
    reasoning: float


class ReplaySegment(BaseModel):
    question: str
    candidate_audio: str
    transcript: str
    evaluation: ReplayEvaluation


class CandidateInterviewReport(BaseModel):
    candidate: Candidate
    interview: InterviewSummary
    questions: List[QuestionBreakdown]
    replay_segments: List[ReplaySegment]


class SkillAnalytics(BaseModel):
    interview_id: str
    skills: Dict[str, float]


class CandidateComparisonRow(BaseModel):
    candidate_id: str
    candidate_name: str
    technical: float
    communication: float
    overall: float
