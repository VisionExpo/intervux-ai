import { StateMachine } from '../StateMachine';

export type ConnectionState = 'Disconnected' | 'Connecting' | 'Connected' | 'Recovering';
export type ConnectionEvent = 'CONNECT' | 'CONNECTED' | 'DISCONNECT' | 'DISCONNECTED';

export const createConnectionMachine = (id: string) => new StateMachine<ConnectionState, ConnectionEvent>(
    id,
    'Disconnected',
    [
        { from: ['Disconnected', 'Recovering'], event: 'CONNECT', to: 'Connecting' },
        { from: ['Connecting', 'Recovering'], event: 'CONNECTED', to: 'Connected' },
        { from: 'Connected', event: 'DISCONNECT', to: 'Disconnected' },
        { from: 'Connected', event: 'DISCONNECTED', to: 'Recovering' },
        { from: ['Connecting', 'Recovering'], event: 'DISCONNECT', to: 'Disconnected' }
    ]
);
