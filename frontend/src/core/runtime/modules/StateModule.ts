import { RuntimeContext } from '../kernel/RuntimeContext';
import type { RuntimeModule, ModuleHealth } from './RuntimeModule';
import { DomainEvent } from '../../events/DomainEvent';
import { StateMachine } from '../../state/StateMachine';
import { createInterviewMachine, type InterviewStage, type InterviewEvent as IMEvent } from '../../state/machines/InterviewMachine';
import { createConnectionMachine, type ConnectionState, type ConnectionEvent } from '../../state/machines/ConnectionMachine';

export class StateModule implements RuntimeModule {
    public readonly id = 'StateModule';
    private interviewMachine!: StateMachine<InterviewStage, IMEvent>;
    private connectionMachine!: StateMachine<ConnectionState, ConnectionEvent>;
    private healthStatus: ModuleHealth = 'initializing';
    private context!: RuntimeContext;
    private unsubscribeAll: (() => void)[] = [];

    public async initialize(context: RuntimeContext): Promise<void> {
        this.context = context;
        this.interviewMachine = createInterviewMachine('core-interview');
        this.connectionMachine = createConnectionMachine('core-connection');
        this.healthStatus = 'healthy';
    }

    public async start(): Promise<void> {
        // Subscribe to relevant domain events to drive state machines
        // e.g. this.unsubscribeAll.push(this.context.eventBus.subscribe(...));
    }

    public async stop(): Promise<void> {
        this.unsubscribeAll.forEach(u => u());
    }

    public async dispose(): Promise<void> {}

    public async handle(event: DomainEvent): Promise<void> {
        // Optionally handle direct calls
    }

    public health(): ModuleHealth {
        return this.healthStatus;
    }

    public snapshot(): any {
        return {
            interviewStage: this.interviewMachine.getState(),
            connectionState: this.connectionMachine.getState()
        };
    }
}
