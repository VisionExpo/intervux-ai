import { WorkspaceType } from "./Workspace";

export type ChapterStatus = "upcoming" | "current" | "completed" | "skipped";

export interface InterviewChapter {
    id: string;
    title: string;
    workspace: WorkspaceType;
    estimatedDuration: number;
    status: ChapterStatus;
}

export interface InterviewFlow {
    chapters: InterviewChapter[];
    activeChapterId: string | null;
    currentQuestionId?: string;
    elapsedTime: number;
    estimatedRemaining: number;
}
