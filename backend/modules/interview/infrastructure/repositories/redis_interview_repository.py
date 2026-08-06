from backend.modules.interview.domain.aggregate import InterviewAggregate
from backend.modules.interview.application.interfaces.interview_repository import InterviewRepository

class RedisInterviewRepository(InterviewRepository):
    """
    Redis-backed repository for fast snapshot retrieval during an active interview session.
    (Stubbed for Sprint 1C)
    """

    def load(self, interview_id: str) -> InterviewAggregate:
        raise NotImplementedError("Redis repository not fully implemented yet.")

    def save(self, aggregate: InterviewAggregate) -> None:
        raise NotImplementedError("Redis repository not fully implemented yet.")

    def exists(self, interview_id: str) -> bool:
        raise NotImplementedError("Redis repository not fully implemented yet.")

    def delete(self, interview_id: str) -> None:
        raise NotImplementedError("Redis repository not fully implemented yet.")
