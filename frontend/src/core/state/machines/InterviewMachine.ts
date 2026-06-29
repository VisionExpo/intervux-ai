import { StateMachine } from '../StateMachine';

export type InterviewStage = 'Resume' | 'Greeting' | 'Interview' | 'Completed';
export type InterviewEvent = 'RESUME_UPLOADED' | 'GREETING_FINISHED' | 'INTERVIEW_COMPLETED';

export const createInterviewMachine = (id: string) => new StateMachine<InterviewStage, InterviewEvent>(
    id,
    'Resume',
    [
        { from: 'Resume', event: 'RESUME_UPLOADED', to: 'Greeting' },
        { from: 'Greeting', event: 'GREETING_FINISHED', to: 'Interview' },
        { from: 'Interview', event: 'INTERVIEW_COMPLETED', to: 'Completed' }
    ]
);
