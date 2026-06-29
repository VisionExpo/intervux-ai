import { RuntimeContext } from '../kernel/RuntimeContext';
import { DomainEvent } from '../../events/DomainEvent';

export type ModuleHealth = 'healthy' | 'degraded' | 'disconnected' | 'initializing' | 'error';

export interface RuntimeModule {
    readonly id: string;
    initialize(context: RuntimeContext): Promise<void>;
    start(): Promise<void>;
    stop(): Promise<void>;
    dispose(): Promise<void>;
    handle(event: DomainEvent): Promise<void>;
    health(): ModuleHealth;
    snapshot?(): any;
}
