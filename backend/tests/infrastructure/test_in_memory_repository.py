import pytest
from modules.interview.domain.aggregate import InterviewAggregate
from modules.interview.infrastructure.repositories.in_memory_interview_repository import InMemoryInterviewRepository, InterviewNotFoundException
from modules.interview.domain.exceptions import StaleAggregateVersionException


def test_in_memory_repo_save_and_load():
    repo = InMemoryInterviewRepository()
    agg = InterviewAggregate.start("Alice", "Backend Engineer")
    
    assert agg.version == 1
    
    # Initial save
    repo.save(agg)
    assert repo.exists(agg.id)
    
    # Load
    loaded_agg = repo.load(agg.id)
    assert loaded_agg.candidate_name == "Alice"
    assert loaded_agg.version == 1

def test_in_memory_repo_optimistic_concurrency():
    repo = InMemoryInterviewRepository()
    agg = InterviewAggregate.start("Bob", "Frontend Engineer")
    repo.save(agg)
    
    # Load a copy
    agg1 = repo.load(agg.id)
    # Load another copy
    agg2 = repo.load(agg.id)
    
    # Mutate agg1
    agg1.parse_resume(["JS", "React"])
    assert agg1.version == 2
    repo.save(agg1) # This should succeed
    
    # Mutate agg2 (which is still at version 1, and expects the repo to have version 0 or 1, wait, repo now has version 2)
    # Let's see: agg2 is loaded at version 1. It mutates to version 2.
    agg2.parse_resume(["Vue"])
    assert agg2.version == 2
    
    # Now when agg2 tries to save, repo has version 2. 
    # The repo check: if aggregate.version (2) <= existing.version (2) -> Stale!
    with pytest.raises(StaleAggregateVersionException):
        repo.save(agg2)

def test_load_not_found():
    repo = InMemoryInterviewRepository()
    with pytest.raises(InterviewNotFoundException):
        repo.load("non-existent-id")
