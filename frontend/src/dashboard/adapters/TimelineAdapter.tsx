import { useInterviewSession } from '../../providers/InterviewSessionProvider';
import { EventTimelineWidget } from '../widgets/EventTimelineWidget';

export const TimelineAdapter = () => {
    const { transcriptMessages } = useInterviewSession();

    const mappedEvents = transcriptMessages.map(msg => ({
        id: msg.id,
        speaker: msg.speaker === 'ai' ? 'AI' as const : 'Candidate' as const,
        text: msg.text
    }));

    return <EventTimelineWidget events={mappedEvents} />;
};
