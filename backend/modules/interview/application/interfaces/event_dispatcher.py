from typing import Protocol, List
from backend.modules.interview.domain.events import DomainEvent

class DomainEventDispatcher(Protocol):
    """
    Interface for publishing Domain Events to external consumers
    (e.g., Projection Pipeline, Analytics, Notifications).
    """

    def publish(self, events: List[DomainEvent]) -> None:
        """Publishes a list of events to the configured bus or listeners."""
        ...
