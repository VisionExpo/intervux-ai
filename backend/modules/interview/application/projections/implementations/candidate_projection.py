from typing import Dict, Any
from backend.modules.interview.domain.aggregate import InterviewAggregate
from ..contracts.projection import Projection
from ..contracts.context import ProjectionContext
from ..contracts.envelope import ProjectionEnvelope

class CandidateProjection(Projection):
    """
    Shapes the InterviewAggregate specifically for the Candidate UI.
    Adheres strictly to the capabilities defined in the ProjectionContext.
    """
    
    @property
    def schema_name(self) -> str:
        return "candidate-insights"
        
    @property
    def schema_version(self) -> int:
        return 1

    def project(self, aggregate: InterviewAggregate, context: ProjectionContext) -> ProjectionEnvelope:
        # Build raw payload components based on capabilities
        
        # 1. Base Info
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
        
        # 2. History / Timeline
        # Candidate only sees history up to what they've answered/are being asked.
        history = []
        for i in range(1, aggregate.current_question_index + 1):
            entry: Dict[str, Any] = {
                "questionIndex": i
            }
            
            # Conditionally include answer text if they submitted it
            if i in aggregate.answers:
                entry["hasAnswer"] = True
                if context.capabilities.show_raw_transcripts:
                    entry["answerTranscript"] = aggregate.answers[i]
            else:
                entry["hasAnswer"] = False
                
            # Conditionally include score/feedback
            if i in aggregate.evaluations:
                if context.capabilities.show_scores:
                    entry["score"] = aggregate.evaluations[i]["score"]
                if context.capabilities.show_internal_reasoning:
                    entry["feedback"] = aggregate.evaluations[i]["feedback"]
                    
            history.append(entry)
            
        payload["history"] = history
        
        # 3. Completion Summary
        if aggregate.state.value == "Completed":
            if context.capabilities.show_scores:
                payload["overallScore"] = aggregate.overall_score
            if context.capabilities.show_internal_reasoning:
                payload["summary"] = aggregate.summary

        # Build Envelope
        return ProjectionEnvelope(
            schema=self.schema_name,
            schema_version=self.schema_version,
            aggregate_version=aggregate.metadata.version,
            projection_version=aggregate.metadata.version, # Syncs 1:1 for now
            payload=payload
        )
