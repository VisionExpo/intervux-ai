from typing import Dict, Any
from backend.modules.interview.domain.aggregate import InterviewAggregate
from ..contracts.projection import Projection
from ..contracts.context import ProjectionContext
from ..contracts.envelope import ProjectionEnvelope

class AnalyticsProjection(Projection):
    """
    Projection tailored for internal analytics engines. 
    Strips PII (Personal Identifiable Information) but retains raw metrics.
    """
    
    @property
    def schema_name(self) -> str:
        return "analytics-metrics"
        
    @property
    def schema_version(self) -> int:
        return 1

    def project(self, aggregate: InterviewAggregate, context: ProjectionContext) -> ProjectionEnvelope:
        payload: Dict[str, Any] = {
            "interviewId": aggregate.metadata.id,
            # Deliberately OMITTING candidateName for PII safety.
            "roleTarget": aggregate.role_target,
            "state": aggregate.state.value,
            "totalQuestionsAsked": aggregate.total_questions_asked
        }
        
        # Analytics cares about scores but not textual feedback
        scores = []
        for i in aggregate.evaluations:
            scores.append(aggregate.evaluations[i]["score"])
            
        payload["scores"] = scores
        if aggregate.state.value == "Completed":
            payload["overallScore"] = aggregate.overall_score

        return ProjectionEnvelope(
            schema=self.schema_name,
            schema_version=self.schema_version,
            aggregate_version=aggregate.metadata.version,
            projection_version=aggregate.metadata.version,
            payload=payload
        )
