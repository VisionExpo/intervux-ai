from backend.modules.interview.domain.aggregate import InterviewAggregate

class AggregateFactory:
    """
    Factory for constructing InterviewAggregate instances in specific states 
    to simplify tests and avoid repetitive mutation boilerplate.
    """
    
    @staticmethod
    def started(candidate_name: str = "Test Candidate", role_target: str = "Test Role") -> InterviewAggregate:
        return InterviewAggregate.start(candidate_name, role_target)
        
    @staticmethod
    def ready_for_questions() -> InterviewAggregate:
        agg = AggregateFactory.started()
        agg.parse_resume(["Python", "Testing"])
        agg.generate_greeting("Hello there!")
        return agg
        
    @staticmethod
    def partially_evaluated() -> InterviewAggregate:
        agg = AggregateFactory.ready_for_questions()
        agg.ask_question("Question 1?")
        agg.record_answer("Answer 1")
        agg.complete_evaluation(0.8, "Good")
        agg.ask_question("Question 2?")
        return agg
        
    @staticmethod
    def completed() -> InterviewAggregate:
        agg = AggregateFactory.partially_evaluated()
        agg.record_answer("Answer 2")
        agg.complete_evaluation(0.9, "Excellent")
        agg.complete_interview("Overall strong performer")
        return agg
