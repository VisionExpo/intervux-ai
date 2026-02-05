from typing import List, Optional, Dict
from pydantic import BaseModel, Field


# =========================================================
# v1.0 MODELS (ACTIVE)
# =========================================================

class Project(BaseModel):
    """
    Represents a single project from the candidate resume.
    Used in resume parsing and question personalization.
    """
    title: str
    tech_stack: List[str] = Field(default_factory=list)
    description: str = ""


class ResumeData(BaseModel):
    """
    Structured resume information extracted from PDF/DOCX.
    """
    name: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)


class AnswerEvaluation(BaseModel):
    """
    Evaluation output for a single interview answer.
    """
    scores: Dict[str, int]               # e.g. {"clarity": 7, "depth": 6}
    feedback: List[str]                  # bullet-level feedback
    summary: Optional[str] = None        # short evaluator summary


class InterviewState:
    """
    In-memory interview session state.

    v1.0 design decisions:
    - Single active session
    - Stateless API, stateful backend object
    - Reset on /start
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.resume_text: Optional[str] = None
        self.profile: Optional[ResumeData] = None
        self.questions: List[str] = []
        self.current_index: int = 0
        self.answers: List[Dict] = []
        self.final_report: Optional[Dict] = None


# =========================================================
# v2+ MODELS (PLANNED — NOT USED IN v1.0)
# =========================================================

class InterviewMessage(BaseModel):
    """
    v2+: Used for multi-turn conversational interviews
    with adaptive follow-ups.
    """
    session_id: str
    text: str


class InterviewResponse(BaseModel):
    """
    v2+: AI response with emotion/context metadata.
    """
    text: str
    emotion: Optional[str] = "neutral"


class EmotionState(BaseModel):
    """
    v2+: Emotion & stress inference from audio/video.
    """
    stress_score: float
    confidence: float
    face_detected: bool


class CodeSubmission(BaseModel):
    """
    v2+: Coding interview input.
    """
    session_id: str
    problem_description: str
    code_snippet: str


class CodeExecutionResult(BaseModel):
    """
    v2+: Code execution & evaluation output.
    """
    output: str
    error: Optional[str] = None