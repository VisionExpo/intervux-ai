import pytest
from backend.modules.interview.domain.aggregate import InterviewAggregate, InterviewState
from backend.modules.interview.domain.exceptions import InvalidStateTransitionException, InvariantViolationException

def test_aggregate_creation():
    agg = InterviewAggregate.start("John Doe", "Software Engineer")
    
    assert agg.candidate_name == "John Doe"
    assert agg.role_target == "Software Engineer"
    assert agg.state == InterviewState.CREATED
    assert agg.metadata.version == 1
    
    events = agg.pull_pending_events()
    assert len(events) == 1
    assert events[0].__class__.__name__ == "InterviewStarted"
    
    # Version should not change on pull
    assert agg.metadata.version == 1
    
    # Second pull should be empty
    assert len(agg.pull_pending_events()) == 0

def test_happy_path_lifecycle():
    agg = InterviewAggregate.start("John Doe", "Software Engineer")
    agg.parse_resume(["Python", "React"])
    agg.generate_greeting("Hello John!")
    agg.ask_question("What is Python?")
    agg.record_answer("It is a language.")
    agg.complete_evaluation(0.9, "Good answer.")
    agg.complete_interview("Strong candidate.")
    
    assert agg.state == InterviewState.COMPLETED
    assert agg.overall_score == 0.9
    assert agg.metadata.version == 7
    
    events = agg.pull_pending_events()
    assert len(events) == 7

def test_invalid_state_transition():
    agg = InterviewAggregate.start("John Doe", "Software Engineer")
    
    # Cannot ask a question directly from CREATED
    with pytest.raises(InvalidStateTransitionException):
        agg.ask_question("What is Python?")
        
    assert agg.metadata.version == 1 # Version should not increment on failure

def test_invariant_evaluation_without_answer():
    agg = InterviewAggregate.start("John Doe", "Software Engineer")
    agg.parse_resume([])
    agg.generate_greeting("Hi")
    agg.ask_question("Question")
    
    # Cannot evaluate without recording an answer first
    # Wait, the state transition check will catch this first (state is QUESTION, evaluate requires RECORDING)
    with pytest.raises(InvalidStateTransitionException):
        agg.complete_evaluation(0.5, "Feedback")
        
    # Let's bypass state to test the specific invariant (though state transition is the primary guard)
    agg.state = InterviewState.RECORDING 
    with pytest.raises(InvariantViolationException, match="Cannot evaluate a question without a recorded answer"):
        agg.complete_evaluation(0.5, "Feedback")

def test_question_monotonicity():
    agg = InterviewAggregate.start("John Doe", "Software Engineer")
    agg.parse_resume([])
    agg.generate_greeting("Hi")
    
    agg.ask_question("Q1")
    assert agg.current_question_index == 1
    
    agg.record_answer("A1")
    agg.complete_evaluation(1.0, "Good")
    
    agg.ask_question("Q2")
    assert agg.current_question_index == 2
    
    # Version should correctly reflect mutations
    assert agg.metadata.version == 7
