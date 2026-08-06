from typing import Dict, Any
from backend.modules.interview.domain.aggregate import InterviewAggregate
from ..contracts.projection import Projection
from ..contracts.context import ProjectionContext
from ..contracts.envelope import ProjectionEnvelope
import time

class TelemetryProjection(Projection):
    """
    Projection for performance monitoring and telemetry.
    Strictly contains timing and event metadata; no domain state.
    """
    
    @property
    def schema_name(self) -> str:
        return "telemetry-heartbeat"
        
    @property
    def schema_version(self) -> int:
        return 1

    def project(self, aggregate: InterviewAggregate, context: ProjectionContext) -> ProjectionEnvelope:
        payload: Dict[str, Any] = {
            "interviewId": aggregate.metadata.id,
            "state": aggregate.state.value,
            "metadata": {
                "version": aggregate.metadata.version,
                "uptime": (time.time() - aggregate.metadata.created_at.timestamp())
            }
        }
        
        return ProjectionEnvelope(
            schema=self.schema_name,
            schema_version=self.schema_version,
            aggregate_version=aggregate.metadata.version,
            projection_version=aggregate.metadata.version,
            payload=payload
        )
