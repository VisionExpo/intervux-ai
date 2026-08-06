import pytest
from backend.modules.interview.application.interview_service import InterviewService
from backend.modules.interview.infrastructure.repositories.in_memory_interview_repository import InMemoryInterviewRepository
from backend.modules.interview.infrastructure.event_dispatcher import InMemoryEventDispatcher
from backend.modules.interview.application.commands import (
    StartInterviewCommand,
    ParseResumeCommand,
    GenerateGreetingCommand
)
from backend.modules.interview.domain.events import InterviewStarted, ResumeParsed, GreetingGenerated


def test_interview_service_start_and_mutate():
    repo = InMemoryInterviewRepository()
    dispatcher = InMemoryEventDispatcher()
    service = InterviewService(repo, dispatcher)
    
    # 1. Start
    start_cmd = StartInterviewCommand(candidate_name="Charlie", role_target="DevOps")
    interview_id = service.execute(start_cmd)
    
    assert repo.exists(interview_id)
    assert len(dispatcher.published_events) == 1
    assert isinstance(dispatcher.published_events[0], InterviewStarted)
    
    # 2. Parse Resume
    parse_cmd = ParseResumeCommand(interview_id=interview_id, extracted_skills=["Docker"])
    service.execute(parse_cmd)
    
    agg = repo.load(interview_id)
    assert agg.metadata.version == 2
    assert len(dispatcher.published_events) == 2
    assert isinstance(dispatcher.published_events[1], ResumeParsed)
    
    # 3. Generate Greeting
    greet_cmd = GenerateGreetingCommand(interview_id=interview_id, greeting_text="Hello")
    service.execute(greet_cmd)
    
    agg = repo.load(interview_id)
    assert agg.metadata.version == 3
    assert len(dispatcher.published_events) == 3
    assert isinstance(dispatcher.published_events[2], GreetingGenerated)
