from typing import Protocol
from backend.modules.interview.domain.events import DomainEvent
from .envelope import ProjectionEnvelope

class ProjectionDelivery(Protocol):
    """
    Infrastructure interface to push completed projection envelopes 
    to external transports (e.g., WebSockets, SSE, REST Cache).
    """
    def deliver(self, envelope: ProjectionEnvelope) -> None:
        ...


class ProjectionSubscriber(Protocol):
    """
    Infrastructure interface that listens for Domain Events 
    and triggers the ProjectionExecutor.
    """
    def handle(self, event: DomainEvent) -> None:
        ...
