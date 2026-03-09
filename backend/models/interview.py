from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field


# =========================================================
# STATE MACHINE
# =========================================================

class InterviewPhase(Enum):
    """
    Interview session phase state machine.
    Used to guard transitions and prevent invalid states.
    """
    CONNECTING = "CONNECTING"
    WAITING_RESUME = "WAITING_RESUME"
    QUESTION = "QUESTION"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    NEXT_QUESTION = "NEXT_QUESTION"
    COMPLETE = "COMPLETE"

    def can_receive(self, message_type: str) -> bool:
        """Check if current phase can receive this message type."""
        transitions = {
            InterviewPhase.WAITING_RESUME: {"resume_upload"},
            InterviewPhase.LISTENING: {"audio_chunk", "stream_end", "audio_end"},
            InterviewPhase.PROCESSING: set(),  # No messages during processing
            InterviewPhase.QUESTION: {"audio_chunk"},
            InterviewPhase.NEXT_QUESTION: set(),  # Handled internally
            InterviewPhase.COMPLETE: set(),  # No more messages
        }
        return message_type in transitions.get(self, set())

    def requires(self, required_phase: "InterviewPhase") -> bool:
        """Check if this phase requires being in a specific phase."""
        return self == required_phase


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


class InterviewMemory:
    """
    Lightweight in-session memory for adaptive questioning.
    """

    def __init__(self):
        self.answers: List[Dict] = []
        self.key_concepts: set[str] = set()
        self.projects: List[str] = []
        self.last_topics: List[str] = []


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
        self.phase: InterviewPhase = InterviewPhase.CONNECTING
        self.resume_text: Optional[str] = None
        self.profile: Optional[ResumeData] = None
        self.questions: List[str] = []
        self.question_skills: List[str] = []
        self.question_strategies: List[str] = []
        self.topics: List[str] = []
        self.concepts: List[str] = []
        self.concept_difficulties: List[int] = []
        self.current_index: int = 0
        self.target_question_count: int = 0
        self.current_difficulty: int = 2
        self.difficulty_engine = None
        self.skill_max_difficulty: Dict[str, int] = {}
        self.skill_map: Dict[str, int] = {}
        self.skill_coverage = None
        self.topic_scores: Dict[str, List[float]] = {}
        self.answers: List[Dict] = []
        self.memory = InterviewMemory()
        self.final_report: Optional[Dict] = None

    def transition_to(self, new_phase: InterviewPhase) -> None:
        """Safely transition to a new phase."""
        # Add validation logic here if needed
        self.phase = new_phase

    def can_proceed(self, message_type: str) -> bool:
        """Check if current phase can handle this message."""
        return self.phase.can_receive(message_type)


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
