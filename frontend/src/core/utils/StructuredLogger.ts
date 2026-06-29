export interface LogEntry {
    timestamp: string;
    session_id: string;
    event_id: string;
    module: string;
    event: string;
    sequence: number;
    latency_ms: number;
    metadata: Record<string, any>;
}

export class StructuredLogger {
    private static sequenceNum = 0;
    private static sessionId = "unknown";

    public static setSessionId(id: string) {
        this.sessionId = id;
    }

    public static log(
        module: string,
        event: string,
        eventId: string,
        latencyMs: number = 0,
        metadata: Record<string, any> = {}
    ) {
        this.sequenceNum++;
        const entry: LogEntry = {
            timestamp: new Date().toISOString(),
            session_id: this.sessionId,
            event_id: eventId,
            module,
            event,
            sequence: this.sequenceNum,
            latency_ms: latencyMs,
            metadata
        };

        // Write structured JSON to console for Observability
        console.log(JSON.stringify(entry));
    }
}
