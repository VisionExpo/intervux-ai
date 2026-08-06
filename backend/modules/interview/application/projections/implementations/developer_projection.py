from typing import Dict, Any
from backend.modules.interview.domain.aggregate import InterviewAggregate
from ..contracts.projection import Projection
from ..contracts.context import ProjectionContext
from ..contracts.envelope import ProjectionEnvelope

class DeveloperProjection(Projection):
    """
    Projection for Developers/Debugging. Includes EVERYTHING in the aggregate
    state, plus debugging metadata if needed.
    """
    
    @property
    def schema_name(self) -> str:
        return "developer-debug"
        
    @property
    def schema_version(self) -> int:
        return 1

    def project(self, aggregate: InterviewAggregate, context: ProjectionContext) -> ProjectionEnvelope:
        payload: Dict[str, Any] = {
            "interviewId": aggregate.metadata.id,
            "candidateName": aggregate.candidate_name,
            "roleTarget": aggregate.role_target,
            "state": aggregate.state.value,
            "progress": {
                "currentQuestionIndex": aggregate.current_question_index,
                "totalQuestionsAsked": aggregate.total_questions_asked
            },
            "evaluations": aggregate.evaluations,
            "answers": aggregate.answers,
            "overallScore": aggregate.overall_score,
            "summary": aggregate.summary
        }
        
        # In a real app, if capabilities allow system_prompts, we might pull them from somewhere.
        if context.capabilities.show_system_prompts:
            payload["system_prompts"] = "MOCK_SYSTEM_PROMPTS_DUMP"

        return ProjectionEnvelope(
            schema=self.schema_name,
            schema_version=self.schema_version,
            aggregate_version=aggregate.metadata.version,
            projection_version=aggregate.metadata.version,
            payload=payload
        )
