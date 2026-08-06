from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class StartInterviewCommand:
    candidate_name: str
    role_target: str

@dataclass(frozen=True)
class ParseResumeCommand:
    interview_id: str
    extracted_skills: List[str]

@dataclass(frozen=True)
class GenerateGreetingCommand:
    interview_id: str
    greeting_text: str

@dataclass(frozen=True)
class AskQuestionCommand:
    interview_id: str
    question_text: str

@dataclass(frozen=True)
class ProcessAnswerCommand:
    interview_id: str
    transcript: str
    
@dataclass(frozen=True)
class EvaluateAnswerCommand:
    interview_id: str
    score: float
    feedback: str

@dataclass(frozen=True)
class CompleteInterviewCommand:
    interview_id: str
    summary: str
