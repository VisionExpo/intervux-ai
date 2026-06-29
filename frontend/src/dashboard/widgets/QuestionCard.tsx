
import { Card, Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

interface QuestionCardProps {
    title?: string;
    question?: string;
    difficulty?: string;
}

export const QuestionCard = ({ title = "Current Question", question = "Loading...", difficulty }: QuestionCardProps) => (
    <Card className="question-card" padding="24px">
        <Stack gap="12px">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ color: theme.text.secondary, fontSize: '0.875rem', fontWeight: 600, textTransform: 'uppercase' }}>
                    {title}
                </div>
                {difficulty && (
                    <div style={{ color: theme.status.info, fontSize: '0.75rem', fontWeight: 600 }}>
                        {difficulty}
                    </div>
                )}
            </div>
            <div style={{ color: theme.text.primary, fontSize: '1.25rem', lineHeight: 1.5 }}>
                {question}
            </div>
        </Stack>
    </Card>
);
