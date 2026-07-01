export interface Disposable {
    dispose(): void;
}

export interface Clock {
    now(): number;
    elapsed(): number;
    schedule(delay: number, callback: () => void): Disposable;
    pause(): void;
    resume(): void;
    speed(multiplier: number): void;
}
