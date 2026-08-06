from typing import Protocol, Any, Dict
from backend.modules.interview.domain.aggregate import InterviewAggregate
from .context import ProjectionContext
from .envelope import ProjectionEnvelope

class Projection(Protocol):
    """
    Base protocol for all projection implementations.
    """
    
    @property
    def schema_name(self) -> str:
        """The identifier of the projection schema (e.g., 'candidate-insights')."""
        ...
        
    @property
    def schema_version(self) -> int:
        """The version of the DTO contract."""
        ...

    def project(self, aggregate: InterviewAggregate, context: ProjectionContext) -> ProjectionEnvelope:
        """
        Transforms the InterviewAggregate into a specific DTO, honoring the context capabilities.
        """
        ...
