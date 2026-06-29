import { StructuredLogger } from '../utils/StructuredLogger';
import { DomainEvent } from './DomainEvent';

type EventHandler<T extends DomainEvent> = (event: T) => void | Promise<void>;

export class EventBus {
    private handlers: Map<string, Set<EventHandler<any>>> = new Map();
    private globalHandlers: Set<EventHandler<any>> = new Set();

    public subscribe<T extends DomainEvent>(eventType: string, handler: EventHandler<T>): () => void {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, new Set());
        }
        this.handlers.get(eventType)!.add(handler);

        return () => {
            const typeHandlers = this.handlers.get(eventType);
            if (typeHandlers) {
                typeHandlers.delete(handler);
                if (typeHandlers.size === 0) {
                    this.handlers.delete(eventType);
                }
            }
        };
    }

    public subscribeAll(handler: EventHandler<any>): () => void {
        this.globalHandlers.add(handler);
        return () => {
            this.globalHandlers.delete(handler);
        };
    }

    public async publish(event: DomainEvent): Promise<void> {
        const startTime = performance.now();
        const promises: Promise<void>[] = [];

        const typeHandlers = this.handlers.get(event.type);
        if (typeHandlers) {
            Array.from(typeHandlers).forEach(handler => {
                promises.push(Promise.resolve(handler(event)).catch(e => {
                    console.error(`Error in event handler for ${event.type}:`, e);
                }));
            });
        }

        this.globalHandlers.forEach(handler => {
            promises.push(Promise.resolve(handler(event)).catch(e => {
                console.error(`Error in global event handler for ${event.type}:`, e);
            }));
        });

        await Promise.allSettled(promises);
        
        const latencyMs = performance.now() - startTime;
        
        // Ensure EventBus observability constraint
        StructuredLogger.log(
            "EventBus",
            event.type,
            (event as any).id || "unknown-id",
            latencyMs,
            { payload: (event as any).payload }
        );
    }
}
