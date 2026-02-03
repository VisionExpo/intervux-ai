from typing import List, Optional
from pydantic import BaseModel


# ---------------------------
# Resume / Candidate Models
# ---------------------------

class Project(BaseModel):
    title: str
    tech_stack: Optional[List[str]] = []
    description: Optional[str] = ""


class ResumeData(BaseModel):
    name: str
    skills: List[str]
    projects: List[Project]


# ---------------------------
# Interview Session Models
# ---------------------------

class InterviewStartRequest(BaseModel):
    session_id: str
    resume: ResumeData
    job_role: str = "AI Engineer"


class InterviewMessage(BaseModel):
    session_id: str
    text: str


class InterviewResponse(BaseModel):
    text: str
    emotion: Optional[str] = "neutral"


# ---------------------------
# Emotion / Stress Models
# ---------------------------

class EmotionState(BaseModel):
    stress_score: float
    confidence: float
    face_detected: bool


# ---------------------------
# Code Interview Models
# ---------------------------

class CodeSubmission(BaseModel):
    session_id: str
    problem_description: str
    code_snippet: str


class CodeExecutionResult(BaseModel):
    output: str
    error: Optional[str] = None
