import pytest
from backend.modules.interview.domain.aggregate import InterviewAggregate, InterviewState
from backend.modules.interview.application.projections.contracts.role import ProjectionRole
from backend.modules.interview.application.projections.contracts.context import ProjectionContext
from backend.modules.interview.application.projections.contracts.capabilities import ProjectionCapabilities
from backend.modules.interview.application.projections.implementations.candidate_projection import CandidateProjection

@pytest.fixture
def sample_aggregate() -> InterviewAggregate:
    agg = InterviewAggregate.start("Alice", "Frontend Engineer")
    agg.parse_resume(["React"])
    agg.generate_greeting("Hi Alice!")
    agg.ask_question("What is the virtual DOM?")
    agg.record_answer("It is a representation of the UI.")
    agg.complete_evaluation(0.9, "Excellent concise answer.")
    # At this point, version = 6
    return agg


def test_candidate_projection_strict_policy(sample_aggregate: InterviewAggregate):
    """
    Test that the projection strips out scores and internal reasoning 
    when capabilities are strictly set to False (default for Candidate).
    """
    projection = CandidateProjection()
    context = ProjectionContext(
        role=ProjectionRole.CANDIDATE,
        capabilities=ProjectionCapabilities(
            show_scores=False,
            show_internal_reasoning=False,
            show_raw_transcripts=False
        )
    )
    
    envelope = projection.project(sample_aggregate, context)
    
    # Assert Envelope Metadata
    assert envelope.schema == "candidate-insights"
    assert envelope.schema_version == 1
    assert envelope.aggregate_version == sample_aggregate.metadata.version
    assert envelope.projection_version == sample_aggregate.metadata.version
    
    # Assert Payload Content
    payload = envelope.payload
    assert payload["candidateName"] == "Alice"
    assert payload["state"] == InterviewState.EVALUATION.value
    assert payload["progress"]["currentQuestionIndex"] == 1
    
    # Assert history does NOT contain sensitive info
    history = payload["history"]
    assert len(history) == 1
    q1 = history[0]
    
    assert q1["questionIndex"] == 1
    assert q1["hasAnswer"] == True
    
    assert "score" not in q1
    assert "feedback" not in q1
    assert "answerTranscript" not in q1


def test_candidate_projection_permissive_policy(sample_aggregate: InterviewAggregate):
    """
    Test that the projection includes everything if capabilities allow it.
    (This proves the projection is just honoring context, not making policy decisions).
    """
    projection = CandidateProjection()
    context = ProjectionContext(
        role=ProjectionRole.DEVELOPER, # Role doesn't matter to projection, capabilities do
        capabilities=ProjectionCapabilities(
            show_scores=True,
            show_internal_reasoning=True,
            show_raw_transcripts=True
        )
    )
    
    envelope = projection.project(sample_aggregate, context)
    payload = envelope.payload
    
    q1 = payload["history"][0]
    assert q1["score"] == 0.9
    assert q1["feedback"] == "Excellent concise answer."
    assert q1["answerTranscript"] == "It is a representation of the UI."
