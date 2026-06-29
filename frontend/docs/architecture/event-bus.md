# Event Bus & Timeline

## Purpose
To decouple event production (e.g., Speech Detected, Face Lost, Code Run) from event consumption (e.g., Analytics, Timeline UI, Logging).

## Concept
All significant actions in the runtime are emitted as standardized `InterviewEvent` objects:
```ts
interface InterviewEvent<T = any> {
    id: string;
    timestamp: number;
    type: string;
    source: 'system' | 'ai' | 'candidate' | 'vision' | 'evaluation';
    payload: T;
    severity: 'info' | 'success' | 'warning' | 'error';
}
```

Features like the `EventTimeline` simply subscribe to this bus. This architecture is essential for our future "Interview Replay" functionality.
