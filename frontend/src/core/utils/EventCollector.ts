import { LogEntry } from './StructuredLogger';

type EventListener = (events: LogEntry[]) => void;

export class EventCollector {
    private static MAX_EVENTS = 500;
    private static events: LogEntry[] = [];
    private static listeners: Set<EventListener> = new Set();

    public static addEvent(entry: LogEntry) {
        this.events.push(entry);
        if (this.events.length > this.MAX_EVENTS) {
            this.events.shift(); // Remove oldest to maintain circular buffer
        }
        
        // Expose globally for Playwright / end-to-end tests
        (window as any).__runtimeEvents = this.events;

        this.notifyListeners();
    }

    public static getEvents(): LogEntry[] {
        return [...this.events];
    }

    public static subscribe(listener: EventListener): () => void {
        this.listeners.add(listener);
        // Fire immediately with current state
        listener([...this.events]);
        
        return () => {
            this.listeners.delete(listener);
        };
    }

    public static clear() {
        this.events = [];
        (window as any).__runtimeEvents = [];
        this.notifyListeners();
    }

    private static notifyListeners() {
        const snapshot = [...this.events];
        this.listeners.forEach(listener => {
            try {
                listener(snapshot);
            } catch (err) {
                console.error("EventCollector listener error:", err);
            }
        });
    }
}
