import pytest
from backend.modules.interview.domain.aggregate import InterviewAggregate
from backend.modules.interview.infrastructure.repositories.in_memory_interview_repository import InMemoryInterviewRepository, InterviewNotFoundException
from backend.modules.interview.domain.exceptions import StaleAggregateVersionException


def test_in_memory_repo_save_and_load():
    repo = InMemoryInterviewRepository()
    agg = InterviewAggregate.start("Alice", "Backend Engineer")
    
    assert agg.metadata.version == 1
    
    # Initial save
    repo.save(agg)
    assert repo.exists(agg.metadata.id)
    
    # Load
    loaded_agg = repo.load(agg.metadata.id)
    assert loaded_agg.candidate_name == "Alice"
    assert loaded_agg.metadata.version == 1

def test_in_memory_repo_optimistic_concurrency():
    repo = InMemoryInterviewRepository()
    agg = InterviewAggregate.start("Bob", "Frontend Engineer")
    repo.save(agg)
    
    # Load a copy
    agg1 = repo.load(agg.metadata.id)
    # Load another copy
    agg2 = repo.load(agg.metadata.id)
    
    # Mutate agg1
    agg1.parse_resume(["JS", "React"])
    assert agg1.metadata.version == 2
    repo.save(agg1) # This should succeed
    
    # Mutate agg2
    agg2.parse_resume(["Vue"])
    assert agg2.metadata.version == 2
    
    # Version conflict
    with pytest.raises(StaleAggregateVersionException):
        repo.save(agg2)

def test_load_not_found():
    repo = InMemoryInterviewRepository()
    with pytest.raises(InterviewNotFoundException):
        repo.load("non-existent-id")
