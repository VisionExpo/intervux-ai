export type StateTransition<S extends string, E extends string> = {
    from: S | S[];
    event: E;
    to: S;
    guard?: () => boolean;
    onTransition?: (from: S, to: S, event: E) => void;
};

export class StateMachine<S extends string, E extends string> {
    private currentState: S;
    public readonly id: string;
    private transitions: StateTransition<S, E>[];

    constructor(
        id: string,
        initialState: S,
        transitions: StateTransition<S, E>[]
    ) {
        this.id = id;
        this.currentState = initialState;
        this.transitions = transitions;
    }

    public getState(): S {
        return this.currentState;
    }

    public canTransition(event: E): boolean {
        return this.transitions.some(t => {
            const matchesFrom = Array.isArray(t.from) ? t.from.includes(this.currentState) : t.from === this.currentState;
            const matchesEvent = t.event === event;
            const passesGuard = t.guard ? t.guard() : true;
            return matchesFrom && matchesEvent && passesGuard;
        });
    }

    public transition(event: E): boolean {
        const validTransition = this.transitions.find(t => {
            const matchesFrom = Array.isArray(t.from) ? t.from.includes(this.currentState) : t.from === this.currentState;
            const matchesEvent = t.event === event;
            const passesGuard = t.guard ? t.guard() : true;
            return matchesFrom && matchesEvent && passesGuard;
        });

        if (validTransition) {
            const fromState = this.currentState;
            this.currentState = validTransition.to;
            if (validTransition.onTransition) {
                validTransition.onTransition(fromState, this.currentState, event);
            }
            return true;
        }

        return false;
    }
}
