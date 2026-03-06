from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class Candidate(BaseModel):
    id: str
    name: str
    email: str
    role: str
    resume_url: str
    created_at: datetime


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
