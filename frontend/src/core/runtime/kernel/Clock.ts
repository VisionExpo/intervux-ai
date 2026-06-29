export class Clock {
    public now(): number {
        return Date.now();
    }

    public elapsed(since: number): number {
        return this.now() - since;
    }

    public timestamp(): number {
        return this.now();
    }
}
