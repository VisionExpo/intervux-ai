import { Clock, Disposable } from "./Clock";

export class RealClock implements Clock {
    private startTime: number;
    private isPaused: boolean = false;
    private pauseTime: number = 0;
    private totalPausedTime: number = 0;
    private timeMultiplier: number = 1.0;

    constructor() {
        this.startTime = Date.now();
    }

    public now(): number {
        return Date.now();
    }

    public elapsed(): number {
        if (this.isPaused) {
            return (this.pauseTime - this.startTime - this.totalPausedTime) * this.timeMultiplier;
        }
        return (this.now() - this.startTime - this.totalPausedTime) * this.timeMultiplier;
    }

    public schedule(delay: number, callback: () => void): Disposable {
        const timeoutId = setTimeout(callback, delay / this.timeMultiplier);
        return {
            dispose: () => clearTimeout(timeoutId)
        };
    }

    public pause(): void {
        if (!this.isPaused) {
            this.isPaused = true;
            this.pauseTime = this.now();
        }
    }

    public resume(): void {
        if (this.isPaused) {
            this.isPaused = false;
            this.totalPausedTime += (this.now() - this.pauseTime);
        }
    }

    public speed(multiplier: number): void {
        this.timeMultiplier = multiplier;
    }
}
