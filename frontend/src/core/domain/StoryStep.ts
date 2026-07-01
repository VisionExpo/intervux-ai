export type StoryCommand = 
    | { type: "StartPreparationCommand"; payload?: any }
    | { type: "TransitionWorkspaceCommand"; payload: { to: string, reason: string } }
    | { type: "SpeakCommand"; payload: { text: string } }
    | { type: "CompleteInterviewCommand"; payload?: any }
    | { type: "EmitEventCommand"; payload: { eventName: string, data: any } };

export interface StoryStep {
    id: string;
    chapterId: string;
    command: StoryCommand;
    waitFor?: string; // event name
    timeout?: number;
    rollback?: StoryCommand;
}
