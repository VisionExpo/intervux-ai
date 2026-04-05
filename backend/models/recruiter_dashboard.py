from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class JobPost(BaseModel):
    id: str
    recruiter_id: Optional[str] = None
    title: str
    description: str
    required_skills: List[str] = []
    experience_level: str
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: str = "full-time"
    location: Optional[str] = None
    interview_focus_areas: List[str] = []
    evaluation_weights: dict = {}
    status: str
    created_at: datetime
    updated_at: datetime
    ai_interview_enabled: bool = False
    interview_limit: Optional[int] = None


class JobPostCreate(BaseModel):
    title: str
    description: str = ""
    experience_level: str = "mid"
    required_skills: List[str] = []
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: str = "full-time"
    location: Optional[str] = None
    interview_focus_areas: List[str] = []
    evaluation_weights: dict = {}
    ai_interview_enabled: bool = False
    interview_limit: Optional[int] = None


class JobPostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    experience_level: Optional[str] = None
    status: Optional[str] = None
    required_skills: Optional[List[str]] = None
    salary_range_min: Optional[int] = None
    salary_range_max: Optional[int] = None
    employment_type: Optional[str] = None
    location: Optional[str] = None
    interview_focus_areas: Optional[List[str]] = None
    evaluation_weights: Optional[dict] = None
    ai_interview_enabled: Optional[bool] = None
    interview_limit: Optional[int] = None


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
