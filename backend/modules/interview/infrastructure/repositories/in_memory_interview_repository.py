import copy
from typing import Dict
from modules.interview.domain.aggregate import InterviewAggregate
from modules.interview.domain.exceptions import StaleAggregateVersionException
from modules.interview.application.interfaces.interview_repository import InterviewRepository

class InterviewNotFoundException(Exception):
    pass

class InMemoryInterviewRepository(InterviewRepository):
    """
    In-memory storage for InterviewAggregate. Ideal for unit tests and rapid prototyping.
    """
    
    def __init__(self):
        self._store: Dict[str, InterviewAggregate] = {}

    def load(self, interview_id: str) -> InterviewAggregate:
        if interview_id not in self._store:
            raise InterviewNotFoundException(f"Interview {interview_id} not found.")
        # Deep copy to prevent accidental reference mutations bypassing aggregate rules
        return copy.deepcopy(self._store[interview_id])

    def save(self, aggregate: InterviewAggregate) -> None:
        existing = self._store.get(aggregate.id)
        
        # Enforce optimistic versioning
        if existing is not None:
            # If the aggregate is new, version might be 1 and existing None.
            # But if it exists, existing.version should be exactly aggregate.version - 1
            # Note: in a real mutation, the aggregate's version has already been incremented.
            # E.g. existing is 1. Aggregate is loaded (1), mutated (2).
            # So aggregate.version (2) > existing.version (1) is required.
            if aggregate.version <= existing.version:
                raise StaleAggregateVersionException(
                    f"Version conflict. Persisted: {existing.version}, Aggregate: {aggregate.version}"
                )
                
        self._store[aggregate.id] = copy.deepcopy(aggregate)

    def exists(self, interview_id: str) -> bool:
        return interview_id in self._store

    def delete(self, interview_id: str) -> None:
        if interview_id in self._store:
            del self._store[interview_id]
