import { CandidateInsightModel } from "../transport/EnvelopeDeserializer";

type Subscriber = (insight: CandidateInsightModel) => void;

export class CandidateProjectionRepository {
    private state: CandidateInsightModel | null = null;
    private subscribers: Set<Subscriber> = new Set();
    
    public update(insight: CandidateInsightModel) {
        // Enforce version monotonicity
        if (this.state && insight.version < this.state.version) {
            console.warn(`Ignoring stale projection: ${insight.version} < ${this.state.version}`);
            return;
        }
        this.state = insight;
        this.notify();
    }
    
    public current(): CandidateInsightModel | null {
        return this.state ? JSON.parse(JSON.stringify(this.state)) : null;
    }
    
    public subscribe(callback: Subscriber): () => void {
        this.subscribers.add(callback);
        if (this.state) {
            callback(this.current()!);
        }
        return () => this.subscribers.delete(callback);
    }
    
    private notify() {
        if (!this.state) return;
        const snap = this.current()!;
        for (const sub of this.subscribers) {
            sub(snap);
        }
    }
}

// Global instance for now, analogous to how we handle other repos
export const candidateRepository = new CandidateProjectionRepository();
