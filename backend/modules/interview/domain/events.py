from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid

@dataclass(frozen=True)
class DomainEvent:
    """Base class for all immutable domain events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class InterviewStarted(DomainEvent):
    interview_id: str
    candidate_name: str
    role_target: str


@dataclass(frozen=True)
class ResumeParsed(DomainEvent):
    interview_id: str
    extracted_skills: list[str]


@dataclass(frozen=True)
class GreetingGenerated(DomainEvent):
    interview_id: str
    greeting_text: str


@dataclass(frozen=True)
class QuestionAsked(DomainEvent):
    interview_id: str
    question_index: int
    question_text: str


@dataclass(frozen=True)
class AnswerRecorded(DomainEvent):
    interview_id: str
    question_index: int
    transcript: str


@dataclass(frozen=True)
class EvaluationCompleted(DomainEvent):
    interview_id: str
    question_index: int
    score: float
    feedback: str


@dataclass(frozen=True)
class InterviewCompleted(DomainEvent):
    interview_id: str
    overall_score: float
    summary: str
