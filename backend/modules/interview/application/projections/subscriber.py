from typing import List, Dict
from backend.modules.interview.domain.events import DomainEvent
from backend.modules.interview.application.interfaces.interview_repository import InterviewRepository
from .contracts.delivery import ProjectionSubscriber
from .contracts.role import ProjectionRole
from .executor import ProjectionExecutor

class InterviewProjectionSubscriber(ProjectionSubscriber):
    """
    Listens to domain events and decides which projections to generate 
    and dispatch via the ProjectionExecutor.
    """
    def __init__(self, executor: ProjectionExecutor, repository: InterviewRepository):
        self.executor = executor
        self.repository = repository
        
        # In a real system, we might route certain events to certain projections.
        # For now, any event triggers an update to the primary views.
        self.default_roles = [
            ProjectionRole.CANDIDATE,
            ProjectionRole.RECRUITER,
            ProjectionRole.TELEMETRY
        ]

    def handle(self, event: DomainEvent) -> None:
        """
        Responds to an event, loads the state, and triggers the projections.
        """
        # Note: If optimistic concurrency failed previously, the event wouldn't be here.
        # So we can safely read from the repository.
        aggregate = self.repository.load(event.aggregate_id)
        
        # Execute the projection pipeline for the default roles
        self.executor.execute(aggregate, roles=self.default_roles)
