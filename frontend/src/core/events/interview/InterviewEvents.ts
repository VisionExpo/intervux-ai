import { DomainEvent } from '../DomainEvent';

export class InterviewStageChangedEvent extends DomainEvent {
    constructor(sessionId: string, newStage: string) {
        super('InterviewStageChanged', 'StateModule', sessionId, { newStage });
    }
}

export class QuestionUpdatedEvent extends DomainEvent {
    constructor(sessionId: string, questionIndex: number, totalQuestions: number) {
        super('QuestionUpdated', 'SessionModule', sessionId, { questionIndex, totalQuestions });
    }
}

export class EvaluationUpdatedEvent extends DomainEvent {
    constructor(sessionId: string, evaluation: any) {
        super('EvaluationUpdated', 'SessionModule', sessionId, { evaluation });
    }
}

export class CandidateUpdatedEvent extends DomainEvent {
    constructor(sessionId: string, candidate: any) {
        super('CandidateUpdated', 'SessionModule', sessionId, { candidate });
    }
}
