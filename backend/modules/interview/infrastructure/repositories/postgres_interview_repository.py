from modules.interview.domain.aggregate import InterviewAggregate
from modules.interview.application.interfaces.interview_repository import InterviewRepository

class PostgresInterviewRepository(InterviewRepository):
    """
    PostgreSQL-backed repository for long-term durable storage of the interview aggregate.
    (Stubbed for Sprint 1C)
    """

    def load(self, interview_id: str) -> InterviewAggregate:
        raise NotImplementedError("Postgres repository not fully implemented yet.")

    def save(self, aggregate: InterviewAggregate) -> None:
        raise NotImplementedError("Postgres repository not fully implemented yet.")

    def exists(self, interview_id: str) -> bool:
        raise NotImplementedError("Postgres repository not fully implemented yet.")

    def delete(self, interview_id: str) -> None:
        raise NotImplementedError("Postgres repository not fully implemented yet.")
