import { DomainEvent } from './DomainEvent';

type EventHandler<T extends DomainEvent> = (event: T) => void | Promise<void>;

export class EventBus {
    private handlers: Map<string, Set<EventHandler<any>>> = new Map();

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

    public async publish(event: DomainEvent): Promise<void> {
        const typeHandlers = this.handlers.get(event.type);
        if (typeHandlers) {
            const promises = Array.from(typeHandlers).map(handler => {
                try {
                    return Promise.resolve(handler(event));
                } catch (e) {
                    console.error(`Error in event handler for ${event.type}:`, e);
                    return Promise.resolve();
                }
            });
            await Promise.allSettled(promises);
        }
    }
}
