import { RuntimeContext } from '../kernel/RuntimeContext';
import type { RuntimeModule, ModuleHealth } from './RuntimeModule';
import { DomainEvent } from '../../events/DomainEvent';
import { QuestionUpdatedEvent, EvaluationUpdatedEvent, CandidateUpdatedEvent } from '../../events/interview/InterviewEvents';

export class SessionModule implements RuntimeModule {
    public readonly id = 'SessionModule';
    private healthStatus: ModuleHealth = 'initializing';
    private context!: RuntimeContext;
    private unsubscribeAll: (() => void)[] = [];

    private questionIndex = 0;
    private totalQuestions = 0;
    private lastEvaluation: any = null;
    private candidate: any = null;

    public async initialize(context: RuntimeContext): Promise<void> {
        this.context = context;
        this.healthStatus = 'healthy';
    }

    public async start(): Promise<void> {
        this.unsubscribeAll.push(
            this.context.eventBus.subscribe('QuestionUpdated', (e) => this.handle(e as DomainEvent)),
            this.context.eventBus.subscribe('EvaluationUpdated', (e) => this.handle(e as DomainEvent)),
            this.context.eventBus.subscribe('CandidateUpdated', (e) => this.handle(e as DomainEvent))
        );
    }

    public async stop(): Promise<void> {
        this.unsubscribeAll.forEach(u => u());
    }

    public async dispose(): Promise<void> {}

    public async handle(event: DomainEvent): Promise<void> {
        if (event instanceof QuestionUpdatedEvent) {
            this.questionIndex = event.payload.questionIndex;
            this.totalQuestions = event.payload.totalQuestions;
        } else if (event instanceof EvaluationUpdatedEvent) {
            this.lastEvaluation = event.payload.evaluation;
        } else if (event instanceof CandidateUpdatedEvent) {
            this.candidate = event.payload.candidate;
        }
    }

    public health(): ModuleHealth {
        return this.healthStatus;
    }

    public snapshot(): any {
        return {
            questionIndex: this.questionIndex,
            totalQuestions: this.totalQuestions,
            lastEvaluation: this.lastEvaluation,
            candidate: this.candidate
        };
    }
}
