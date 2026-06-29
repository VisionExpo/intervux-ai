import { Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

interface EventTimelineProps {
    events: {
        id: string;
        speaker: 'AI' | 'Candidate';
        text: string;
    }[];
}

export const EventTimelineWidget = ({ events }: EventTimelineProps) => (
    <div className="event-timeline-widget" style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
        <Stack gap="24px">
            <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                Interview Timeline
            </div>
            {events.map((event, index) => (
                <div key={event.id}>
                    <div style={{ 
                        color: event.speaker === 'AI' ? theme.interview.ai : theme.interview.candidate, 
                        fontWeight: 600, 
                        fontSize: '0.875rem',
                        marginBottom: '4px' 
                    }}>
                        {event.speaker}
                    </div>
                    <div style={{ color: theme.text.primary, fontSize: '0.9375rem', lineHeight: 1.5 }}>
                        {event.text}
                    </div>
                    {index < events.length - 1 && (
                        <div style={{ height: '1px', backgroundColor: theme.border.default, width: '100%', marginTop: '24px' }} />
                    )}
                </div>
            ))}
        </Stack>
    </div>
);
