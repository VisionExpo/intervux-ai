from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class CandidateSignup(BaseModel):
    email: str
    password: str
    name: str


class CandidateProfileResponse(BaseModel):
    id: int
    user_id: str
    name: str
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    resume_url: Optional[str] = None
    resume_score: Optional[float] = None
    interview_score: Optional[float] = None
    profile_score: Optional[float] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    mock_interviews_remaining: int
    created_at: datetime


class CandidateProfileUpdate(BaseModel):
    name: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    education: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None


class ResumeUploadResponse(BaseModel):
    resume_url: str
    resume_score: float
    skills: List[str]
    strengths: List[str]
    weaknesses: List[str]


class MockInterviewResponse(BaseModel):
    id: int
    session_id: str
    score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    reasoning_score: Optional[float] = None
    status: str
    interview_number: int
    created_at: datetime
    completed_at: Optional[datetime] = None


class MockInterviewStartResponse(BaseModel):
    session_id: str
    message: str
    mock_interview_id: int


class NotificationResponse(BaseModel):
    id: int
    type: str
    message: str
    is_read: bool
    created_at: datetime


class DashboardResponse(BaseModel):
    profile_score: float
    resume_score: float
    mock_interview_score: float
    mock_interviews_remaining: int
    recent_activity: List[str]
