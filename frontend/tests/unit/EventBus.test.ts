import { describe, it, expect, vi } from 'vitest';
import { EventBus } from '../../src/core/events/EventBus';
import { DomainEvent } from '../../src/core/events/DomainEvent';
import { EventCollector } from '../../src/core/utils/EventCollector';

class TestEvent extends DomainEvent {
    constructor(public payload: any) {
        super('TEST_EVENT', payload);
    }
}

describe('EventBus', () => {
    it('should publish and subscribe to events', async () => {
        const bus = new EventBus();
        const handler = vi.fn();

        bus.subscribe('TEST_EVENT', handler);
        await bus.publish(new TestEvent({ foo: 'bar' }));

        expect(handler).toHaveBeenCalledTimes(1);
        expect(handler).toHaveBeenCalledWith(expect.objectContaining({ type: 'TEST_EVENT' }));
    });

    it('should unsubscribe correctly', async () => {
        const bus = new EventBus();
        const handler = vi.fn();

        const unsubscribe = bus.subscribe('TEST_EVENT', handler);
        unsubscribe();
        
        await bus.publish(new TestEvent({}));

        expect(handler).not.toHaveBeenCalled();
    });

    it('should support subscribeAll (wildcard equivalent)', async () => {
        const bus = new EventBus();
        const globalHandler = vi.fn();

        bus.subscribeAll(globalHandler);
        await bus.publish(new TestEvent({}));

        expect(globalHandler).toHaveBeenCalledTimes(1);
    });

    it('should record event latency into the EventCollector', async () => {
        const bus = new EventBus();
        EventCollector.clear();
        
        await bus.publish(new TestEvent({ test: 123 }));
        
        const events = EventCollector.getEvents();
        expect(events.length).toBeGreaterThan(0);
        
        const last = events[events.length - 1];
        expect(last.module).toBe('EventBus');
        expect(last.event).toBe('TEST_EVENT');
        expect(last.latency_ms).toBeDefined();
    });
});
