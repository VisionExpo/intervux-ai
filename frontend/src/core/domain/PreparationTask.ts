export type PreparationTaskState = "waiting" | "running" | "completed" | "failed";

export interface PreparationTask {
    id: string;
    title: string;
    state: PreparationTaskState;
}

export interface PreparationSequence {
    tasks: PreparationTask[];
    overallStatus: "pending" | "active" | "finished" | "failed";
}
