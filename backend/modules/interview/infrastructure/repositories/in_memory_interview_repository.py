import copy
from typing import Dict
from backend.modules.interview.domain.aggregate import InterviewAggregate
from backend.modules.interview.domain.exceptions import StaleAggregateVersionException
from backend.modules.interview.application.interfaces.interview_repository import InterviewRepository

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
        existing = self._store.get(aggregate.metadata.id)
        
        # Enforce optimistic versioning
        if existing is not None:
            if aggregate.metadata.version <= existing.metadata.version:
                raise StaleAggregateVersionException(
                    f"Version conflict. Persisted: {existing.metadata.version}, Aggregate: {aggregate.metadata.version}"
                )
                
        self._store[aggregate.metadata.id] = copy.deepcopy(aggregate)

    def exists(self, interview_id: str) -> bool:
        return interview_id in self._store

    def delete(self, interview_id: str) -> None:
        if interview_id in self._store:
            del self._store[interview_id]
