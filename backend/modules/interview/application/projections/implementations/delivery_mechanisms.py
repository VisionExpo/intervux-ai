from typing import List
from ..contracts.delivery import ProjectionDelivery
from ..contracts.envelope import ProjectionEnvelope

class NullDelivery(ProjectionDelivery):
    """
    A delivery mechanism that discards the envelope. 
    Useful for testing ProjectionExecutor locally without side effects.
    """
    def deliver(self, envelope: ProjectionEnvelope) -> None:
        pass


class MemoryDelivery(ProjectionDelivery):
    """
    A delivery mechanism that stores envelopes in memory.
    Useful for testing that the executor dispatched exactly the expected envelopes.
    """
    def __init__(self):
        self.delivered_envelopes: List[ProjectionEnvelope] = []
        
    def deliver(self, envelope: ProjectionEnvelope) -> None:
        self.delivered_envelopes.append(envelope)
        
    def clear(self) -> None:
        self.delivered_envelopes.clear()
