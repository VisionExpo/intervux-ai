import { RuntimeContext } from '../kernel/RuntimeContext';
import type { RuntimeModule, ModuleHealth } from './RuntimeModule';
import { DomainEvent } from '../../events/DomainEvent';

export class EventRecorder implements RuntimeModule {
    public readonly id = 'EventRecorder';
    private healthStatus: ModuleHealth = 'initializing';
    private context!: RuntimeContext;
    private events: DomainEvent[] = [];
    private unsubscribe!: () => void;

    public async initialize(context: RuntimeContext): Promise<void> {
        this.context = context;
        this.healthStatus = 'healthy';
    }

    public async start(): Promise<void> {
        this.unsubscribe = this.context.eventBus.subscribeAll((event) => this.handle(event));
    }

    public async stop(): Promise<void> {
        if (this.unsubscribe) {
            this.unsubscribe();
        }
    }

    public async dispose(): Promise<void> {
        this.events = [];
    }

    public async handle(event: DomainEvent): Promise<void> {
        this.events.push(event);
    }

    public health(): ModuleHealth {
        return this.healthStatus;
    }

    public snapshot(): any {
        return {
            recordedEventsCount: this.events.length,
            events: this.events 
        };
    }
}
