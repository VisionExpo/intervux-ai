import { InterviewChapter } from "./InterviewChapter";
import { StoryStep } from "./StoryStep";

export interface Scenario {
    id: string;
    title: string;
    candidate: {
        name: string;
        roleTarget: string;
        experienceLevel: string;
    };
    chapters: InterviewChapter[];
    steps: StoryStep[];
    completionReport?: any;
}

export interface ScenarioProvider {
    loadScenario(id: string): Promise<Scenario>;
}
