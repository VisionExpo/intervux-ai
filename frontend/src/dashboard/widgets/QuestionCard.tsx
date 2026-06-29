
import { Card, Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

export const QuestionCard = () => (
    <Card className="question-card" padding="24px">
        <Stack gap="12px">
            <div style={{ color: theme.text.secondary, fontSize: '0.875rem', fontWeight: 600, textTransform: 'uppercase' }}>
                Current Question
            </div>
            <div style={{ color: theme.text.primary, fontSize: '1.25rem', lineHeight: 1.5 }}>
                {/* Placeholder content */}
                What is a context manager in Python? When would you choose to use one over a standard try/finally block?
            </div>
        </Stack>
    </Card>
);
