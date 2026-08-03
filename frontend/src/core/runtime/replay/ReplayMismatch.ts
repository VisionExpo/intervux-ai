export class ReplayMismatchError extends Error {
    public tick: number;
    public phase: "command" | "event" | "snapshot";
    public expectedHash: string;
    public actualHash: string;

    constructor(tick: number, phase: "command" | "event" | "snapshot", expectedHash: string, actualHash: string) {
        super(`Replay Mismatch at Tick ${tick} during phase '${phase}'. Expected ${expectedHash.substring(0,8)}... but got ${actualHash.substring(0,8)}...`);
        this.name = "ReplayMismatchError";
        this.tick = tick;
        this.phase = phase;
        this.expectedHash = expectedHash;
        this.actualHash = actualHash;
    }
}
