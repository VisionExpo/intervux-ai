import { DomainEvent } from '../DomainEvent';

export class ConnectionStateChangedEvent extends DomainEvent {
    constructor(sessionId: string, newState: string) {
        super('ConnectionStateChanged', 'StateModule', sessionId, { newState });
    }
}
