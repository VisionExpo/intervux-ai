import uuid
from typing import List, Optional
from enum import Enum

from .events import (
    DomainEvent,
    InterviewStarted,
    ResumeParsed,
    GreetingGenerated,
    QuestionAsked,
    AnswerRecorded,
    EvaluationCompleted,
    InterviewCompleted
)
from .exceptions import InvalidStateTransitionException, InvariantViolationException
from .value_objects import AggregateMetadata


class InterviewState(Enum):
    CREATED = "Created"
    RESUME_PARSED = "ResumeParsed"
    GREETING = "Greeting"
    QUESTION = "Question"
    RECORDING = "Recording"
    EVALUATION = "Evaluation"
    COMPLETED = "Completed"


class InterviewAggregate:
    """
    The central aggregate root for an interview session.
    Enforces all invariants and state transitions.
    """

    def __init__(self, metadata: AggregateMetadata):
        self.metadata = metadata
        self.state = InterviewState.CREATED
        
        # Candidate Info
        self.candidate_name: Optional[str] = None
        self.role_target: Optional[str] = None
        
        # Progress
        self.current_question_index = 0
        self.total_questions_asked = 0
        
        # Internal Queues
        self._pending_events: List[DomainEvent] = []
        
        # Basic evaluation tracking
        self.evaluations: dict[int, dict] = {}
        self.answers: dict[int, str] = {}
        
        self.overall_score: float = 0.0
        self.summary: str = ""

    # --- Optimistic Versioning ---
    def _increment_version(self):
        self.metadata = self.metadata.increment_version()

    # --- Event Queuing ---
    def _apply(self, event_class, **kwargs):
        """Helper to append an event with aggregate metadata."""
        self._increment_version()
        event = event_class(
            aggregate_id=self.metadata.id,
            version=self.metadata.version,
            **kwargs
        )
        self._pending_events.append(event)

    def pull_pending_events(self) -> List[DomainEvent]:
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events

    # --- Factory / Commands ---

    @classmethod
    def start(cls, candidate_name: str, role_target: str) -> "InterviewAggregate":
        metadata = AggregateMetadata()
        aggregate = cls(metadata=metadata)
        aggregate.candidate_name = candidate_name
        aggregate.role_target = role_target
        aggregate.state = InterviewState.CREATED
        
        aggregate._apply(
            InterviewStarted,
            candidate_name=candidate_name,
            role_target=role_target
        )
        return aggregate

    def parse_resume(self, extracted_skills: List[str]):
        if self.state != InterviewState.CREATED:
            raise InvalidStateTransitionException(f"Cannot parse resume from {self.state}")
        
        self.state = InterviewState.RESUME_PARSED
        self._apply(ResumeParsed, extracted_skills=extracted_skills)

    def generate_greeting(self, greeting_text: str):
        if self.state != InterviewState.RESUME_PARSED:
            raise InvalidStateTransitionException(f"Cannot generate greeting from {self.state}")
        
        self.state = InterviewState.GREETING
        self._apply(GreetingGenerated, greeting_text=greeting_text)

    def ask_question(self, question_text: str):
        if self.state not in [InterviewState.GREETING, InterviewState.EVALUATION]:
            raise InvalidStateTransitionException(f"Cannot ask question from {self.state}")
        
        self.current_question_index += 1
        self.total_questions_asked += 1
        self.state = InterviewState.QUESTION
        
        self._apply(
            QuestionAsked,
            question_index=self.current_question_index,
            question_text=question_text
        )

    def record_answer(self, transcript: str):
        if self.state != InterviewState.QUESTION:
            raise InvalidStateTransitionException(f"Cannot record answer from {self.state}")
        
        self.answers[self.current_question_index] = transcript
        self.state = InterviewState.RECORDING
        
        self._apply(
            AnswerRecorded,
            question_index=self.current_question_index,
            transcript=transcript
        )

    def complete_evaluation(self, score: float, feedback: str):
        if self.state != InterviewState.RECORDING:
            raise InvalidStateTransitionException(f"Cannot evaluate from {self.state}")
            
        # Invariant 5: Evaluation cannot exist without an answer
        if self.current_question_index not in self.answers:
            raise InvariantViolationException("Cannot evaluate a question without a recorded answer.")

        self.evaluations[self.current_question_index] = {"score": score, "feedback": feedback}
        self.state = InterviewState.EVALUATION
        
        self._apply(
            EvaluationCompleted,
            question_index=self.current_question_index,
            score=score,
            feedback=feedback
        )

    def complete_interview(self, summary: str):
        if self.state != InterviewState.EVALUATION:
            raise InvalidStateTransitionException(f"Cannot complete interview from {self.state}")
            
        # Calculate overall score based on available evaluations
        if len(self.evaluations) > 0:
            total = sum(e["score"] for e in self.evaluations.values())
            self.overall_score = total / len(self.evaluations)
            
        self.summary = summary
        self.state = InterviewState.COMPLETED
        
        self._apply(
            InterviewCompleted,
            overall_score=self.overall_score,
            summary=summary
        )
