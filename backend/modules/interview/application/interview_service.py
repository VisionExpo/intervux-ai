from typing import Union
from backend.modules.interview.domain.aggregate import InterviewAggregate
from backend.modules.interview.application.interfaces.interview_repository import InterviewRepository
from backend.modules.interview.application.interfaces.event_dispatcher import DomainEventDispatcher
from backend.modules.interview.application.commands import (
    StartInterviewCommand,
    ParseResumeCommand,
    GenerateGreetingCommand,
    AskQuestionCommand,
    ProcessAnswerCommand,
    EvaluateAnswerCommand,
    CompleteInterviewCommand
)

class InterviewService:
    """
    Application Service orchestrating the Interview bounded context.
    Loads aggregates, executes commands, saves state, and dispatches events.
    """

    def __init__(self, repository: InterviewRepository, dispatcher: DomainEventDispatcher):
        self.repository = repository
        self.dispatcher = dispatcher

    def execute(self, command: Union[StartInterviewCommand, ParseResumeCommand, GenerateGreetingCommand, AskQuestionCommand, ProcessAnswerCommand, EvaluateAnswerCommand, CompleteInterviewCommand]) -> str:
        """
        Executes a command and returns the aggregate ID.
        """
        
        # 1. Load or Create Aggregate
        if isinstance(command, StartInterviewCommand):
            aggregate = InterviewAggregate.start(command.candidate_name, command.role_target)
        else:
            aggregate = self.repository.load(command.interview_id)

        # 2. Mutate state via Domain Aggregate
        if isinstance(command, ParseResumeCommand):
            aggregate.parse_resume(command.extracted_skills)
        elif isinstance(command, GenerateGreetingCommand):
            aggregate.generate_greeting(command.greeting_text)
        elif isinstance(command, AskQuestionCommand):
            aggregate.ask_question(command.question_text)
        elif isinstance(command, ProcessAnswerCommand):
            aggregate.record_answer(command.transcript)
        elif isinstance(command, EvaluateAnswerCommand):
            aggregate.complete_evaluation(command.score, command.feedback)
        elif isinstance(command, CompleteInterviewCommand):
            aggregate.complete_interview(command.summary)

        # 3. Extract Domain Events
        pending_events = aggregate.pull_pending_events()

        # 4. Save Aggregate (Optimistic concurrency enforced here)
        self.repository.save(aggregate)

        # 5. Dispatch Domain Events
        if pending_events:
            self.dispatcher.publish(pending_events)
            
        return aggregate.metadata.id
