from typing import Protocol

from backend.modules.interview.domain.aggregate import InterviewAggregate

class InterviewRepository(Protocol):
    """
    Core repository interface for saving and loading the InterviewAggregate.
    """

    def load(self, interview_id: str) -> InterviewAggregate:
        """Loads an aggregate by ID. Raises exception if not found."""
        ...

    def save(self, aggregate: InterviewAggregate) -> None:
        """
        Saves the aggregate. 
        Must enforce optimistic versioning (reject if current persisted version != aggregate.version - 1).
        """
        ...

    def exists(self, interview_id: str) -> bool:
        """Returns True if the aggregate exists."""
        ...

    def delete(self, interview_id: str) -> None:
        """Hard deletes the aggregate."""
        ...
