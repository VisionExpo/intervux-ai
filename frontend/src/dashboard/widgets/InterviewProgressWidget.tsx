import { Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

export interface InterviewProgressProps {
    currentQuestion: number;
    totalQuestions: number;
    timeElapsed?: string; 
    difficulty?: string;
}

export const InterviewProgressWidget = ({ currentQuestion, totalQuestions, timeElapsed = "00:00", difficulty = "Medium" }: InterviewProgressProps) => (
    <Stack gap="24px" className="interview-progress-widget" style={{ padding: '24px' }}>
        <Stack gap="8px">
            <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Question</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: theme.text.primary }}>
                {currentQuestion} <span style={{ color: theme.text.muted }}>/ {totalQuestions}</span>
            </div>
        </Stack>
        <div style={{ height: '1px', backgroundColor: theme.border.default, width: '100%' }} />
        
        <Stack gap="8px">
            <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Time</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: theme.text.primary, fontFamily: 'monospace' }}>
                {timeElapsed}
            </div>
        </Stack>
        <div style={{ height: '1px', backgroundColor: theme.border.default, width: '100%' }} />
        
        <Stack gap="8px">
            <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Difficulty</div>
            <div style={{ color: theme.status.warning, fontWeight: 500 }}>
                {difficulty}
            </div>
        </Stack>
    </Stack>
);
