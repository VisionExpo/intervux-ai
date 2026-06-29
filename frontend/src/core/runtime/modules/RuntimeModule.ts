import { RuntimeContext } from '../kernel/RuntimeContext';
import { DomainEvent } from '../../events/DomainEvent';

export interface RuntimeModule {
    readonly id: string;
    initialize(context: RuntimeContext): Promise<void>;
    start(): Promise<void>;
    stop(): Promise<void>;
    dispose(): Promise<void>;
    handle(event: DomainEvent): Promise<void>;
}
