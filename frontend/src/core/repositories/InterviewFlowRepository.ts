import { InterviewFlow, InterviewChapter } from "../domain/InterviewChapter";

type Subscriber = (flow: InterviewFlow) => void;

export class InterviewFlowRepository {
    private state: InterviewFlow;
    private subscribers: Set<Subscriber> = new Set();

    constructor() {
        this.state = {
            chapters: [],
            activeChapterId: null,
            elapsedTime: 0,
            estimatedRemaining: 0
        };
    }

    public current(): InterviewFlow {
        // Return defensive copy
        return JSON.parse(JSON.stringify(this.state));
    }

    public subscribe(callback: Subscriber): () => void {
        this.subscribers.add(callback);
        // Immediate callback with current state
        callback(this.current());
        return () => this.subscribers.delete(callback);
    }

    private notify() {
        const snap = this.current();
        for (const sub of this.subscribers) {
            sub(snap);
        }
    }

    public load(chapters: InterviewChapter[]) {
        this.state.chapters = chapters;
        this.state.activeChapterId = chapters.length > 0 ? chapters[0].id : null;
        if (this.state.activeChapterId) {
            this.state.chapters[0].status = "current";
        }
        this.notify();
    }

    public advanceChapter() {
        if (!this.state.activeChapterId) return;

        const currentIndex = this.state.chapters.findIndex(c => c.id === this.state.activeChapterId);
        if (currentIndex === -1 || currentIndex >= this.state.chapters.length - 1) return;

        // Complete current
        this.state.chapters[currentIndex].status = "completed";
        
        // Advance
        const nextChapter = this.state.chapters[currentIndex + 1];
        nextChapter.status = "current";
        this.state.activeChapterId = nextChapter.id;
        
        this.notify();
    }

    public completeChapter() {
        if (!this.state.activeChapterId) return;
        const currentIndex = this.state.chapters.findIndex(c => c.id === this.state.activeChapterId);
        if (currentIndex !== -1) {
            this.state.chapters[currentIndex].status = "completed";
            this.notify();
        }
    }

    public reset() {
        this.state = {
            chapters: [],
            activeChapterId: null,
            elapsedTime: 0,
            estimatedRemaining: 0
        };
        this.notify();
    }

    public updateTiming(elapsed: number, remaining: number) {
        this.state.elapsedTime = elapsed;
        this.state.estimatedRemaining = remaining;
        this.notify();
    }
}
