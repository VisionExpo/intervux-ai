import copy
from typing import Dict, List
from backend.modules.interview.application.interfaces.event_dispatcher import DomainEventDispatcher
from backend.modules.interview.domain.events import DomainEvent

class NullEventDispatcher(DomainEventDispatcher):
    """
    A dispatcher that explicitly does nothing.
    Used for testing or before the Projection Pipeline is implemented.
    """

    def publish(self, events: List[DomainEvent]) -> None:
        pass


class InMemoryEventDispatcher(DomainEventDispatcher):
    """
    A dispatcher that stores events in memory for test assertions.
    """

    def __init__(self):
        self.published_events: List[DomainEvent] = []

    def publish(self, events: List[DomainEvent]) -> None:
        # Deep copy to ensure immutability in tests
        self.published_events.extend(copy.deepcopy(events))

    def clear(self):
        self.published_events.clear()
