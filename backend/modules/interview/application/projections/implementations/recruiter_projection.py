from typing import Dict, Any
from backend.modules.interview.domain.aggregate import InterviewAggregate
from ..contracts.projection import Projection
from ..contracts.context import ProjectionContext
from ..contracts.envelope import ProjectionEnvelope

class RecruiterProjection(Projection):
    """
    Projection tailored for Recruiters. Includes comprehensive history and scores,
    but hides developer-level system prompts.
    """
    
    @property
    def schema_name(self) -> str:
        return "recruiter-dossier"
        
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
            }
        }
        
        history = []
        for i in range(1, aggregate.current_question_index + 1):
            entry: Dict[str, Any] = {
                "questionIndex": i
            }
            
            if i in aggregate.answers and context.capabilities.show_raw_transcripts:
                entry["answerTranscript"] = aggregate.answers[i]
                
            if i in aggregate.evaluations:
                if context.capabilities.show_scores:
                    entry["score"] = aggregate.evaluations[i]["score"]
                if context.capabilities.show_internal_reasoning:
                    entry["feedback"] = aggregate.evaluations[i]["feedback"]
                    
            history.append(entry)
            
        payload["history"] = history
        
        if aggregate.state.value == "Completed":
            if context.capabilities.show_scores:
                payload["overallScore"] = aggregate.overall_score
            if context.capabilities.show_internal_reasoning:
                payload["summary"] = aggregate.summary

        return ProjectionEnvelope(
            schema=self.schema_name,
            schema_version=self.schema_version,
            aggregate_version=aggregate.metadata.version,
            projection_version=aggregate.metadata.version,
            payload=payload
        )
