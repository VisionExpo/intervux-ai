export interface DomainEventPayload {
    [key: string]: any;
}

export abstract class DomainEvent {
    public readonly type: string;
    public readonly timestamp: number;
    public readonly sessionId: string;
    public readonly sequenceNumber: number;
    public readonly source: string;
    public readonly payload: DomainEventPayload;

    private static sequenceCounter = 0;

    constructor(
        type: string,
        source: string,
        sessionId: string,
        payload: DomainEventPayload = {},
        timestamp?: number
    ) {
        this.type = type;
        this.source = source;
        this.sessionId = sessionId;
        this.payload = payload;
        this.timestamp = timestamp ?? Date.now();
        this.sequenceNumber = ++DomainEvent.sequenceCounter;
    }
}
