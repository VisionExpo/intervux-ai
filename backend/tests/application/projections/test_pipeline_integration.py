import pytest
from backend.modules.interview.application.interview_service import InterviewService
from backend.modules.interview.infrastructure.repositories.in_memory_interview_repository import InMemoryInterviewRepository
from backend.modules.interview.infrastructure.event_dispatcher import InMemoryEventDispatcher
from backend.modules.interview.application.commands import StartInterviewCommand, ParseResumeCommand

from backend.modules.interview.application.projections.executor import ProjectionExecutor
from backend.modules.interview.application.projections.registry import ProjectionRegistry
from backend.modules.interview.application.projections.policy_resolver import ProjectionPolicyResolver
from backend.modules.interview.application.projections.contracts.role import ProjectionRole
from backend.modules.interview.application.projections.implementations.candidate_projection import CandidateProjection


def test_end_to_end_projection_pipeline():
    # 1. Setup Write Side
    repo = InMemoryInterviewRepository()
    dispatcher = InMemoryEventDispatcher()
    service = InterviewService(repo, dispatcher)
    
    # 2. Setup Read Side (Projection Pipeline)
    registry = ProjectionRegistry()
    registry.register(ProjectionRole.CANDIDATE, CandidateProjection())
    
    policy_resolver = ProjectionPolicyResolver()
    executor = ProjectionExecutor(registry, policy_resolver)
    
    # 3. Execute Commands
    interview_id = service.execute(StartInterviewCommand("Bob", "Backend"))
    service.execute(ParseResumeCommand(interview_id, ["Python", "DDD"]))
    
    # 4. Verify Domain Events Dispatched
    assert len(dispatcher.published_events) == 2
    assert dispatcher.published_events[1].__class__.__name__ == "ResumeParsed"
    
    # 5. Execute Projection Pipeline
    # Load aggregate (In a real system, the ProjectionSubscriber would receive the event
    # and load the aggregate to project it, or the aggregate state would be passed along)
    aggregate = repo.load(interview_id)
    
    envelope_list = executor.execute(aggregate, [ProjectionRole.CANDIDATE])
    
    # 6. Verify Projection Output
    assert envelope_list is not None
    assert len(envelope_list) == 1
    
    envelope = envelope_list[0]
    assert envelope.schema == "candidate-insights"
    assert envelope.payload["candidateName"] == "Bob"
    assert envelope.payload["roleTarget"] == "Backend"
    assert envelope.payload["state"] == "ResumeParsed"
    assert envelope.aggregate_version == 2
    assert envelope.projection_version == 2
