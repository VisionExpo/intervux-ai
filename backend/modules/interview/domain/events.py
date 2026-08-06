from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid

@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base class for all immutable domain events."""
    aggregate_id: str
    version: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True, kw_only=True)
class InterviewStarted(DomainEvent):
    candidate_name: str
    role_target: str


@dataclass(frozen=True, kw_only=True)
class ResumeParsed(DomainEvent):
    extracted_skills: list[str]


@dataclass(frozen=True, kw_only=True)
class GreetingGenerated(DomainEvent):
    greeting_text: str


@dataclass(frozen=True, kw_only=True)
class QuestionAsked(DomainEvent):
    question_index: int
    question_text: str


@dataclass(frozen=True, kw_only=True)
class AnswerRecorded(DomainEvent):
    question_index: int
    transcript: str


@dataclass(frozen=True, kw_only=True)
class EvaluationCompleted(DomainEvent):
    question_index: int
    score: float
    feedback: str


@dataclass(frozen=True, kw_only=True)
class InterviewCompleted(DomainEvent):
    overall_score: float
    summary: str
