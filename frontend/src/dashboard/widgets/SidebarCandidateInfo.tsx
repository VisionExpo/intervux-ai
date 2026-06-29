import { Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

interface SidebarCandidateInfoProps {
    currentQuestion: number;
    totalQuestions: number;
    timeElapsed: string;
    difficulty: string;
    candidateName: string;
    role: string;
    skills: string[];
}

export const SidebarCandidateInfo = ({ currentQuestion, totalQuestions, timeElapsed, difficulty, candidateName, role, skills }: SidebarCandidateInfoProps) => (
    <Stack gap="24px" className="sidebar-candidate-info" style={{ padding: '24px' }}>
        <Section title="Question">
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: theme.text.primary }}>
                {currentQuestion} <span style={{ color: theme.text.muted }}>/ {totalQuestions}</span>
            </div>
        </Section>
        <Divider />
        
        <Section title="Time">
            <div style={{ fontSize: '1.25rem', fontWeight: 600, color: theme.text.primary, fontFamily: 'monospace' }}>
                {timeElapsed}
            </div>
        </Section>
        <Divider />
        
        <Section title="Difficulty">
            <div style={{ color: theme.status.warning, fontWeight: 500 }}>
                {difficulty}
            </div>
        </Section>
        <Divider />
        
        <Section title="Candidate">
            <Stack gap="12px">
                <div>
                    <div style={{ fontWeight: 600, color: theme.text.primary, fontSize: '1.125rem' }}>{candidateName}</div>
                    <div style={{ color: theme.text.secondary, fontSize: '0.875rem' }}>{role}</div>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {skills.map(skill => (
                        <div key={skill} style={{ padding: '4px 8px', backgroundColor: theme.surface.elevated, borderRadius: theme.radius.sm, fontSize: '0.75rem', color: theme.text.secondary }}>
                            {skill}
                        </div>
                    ))}
                </div>
            </Stack>
        </Section>
    </Stack>
);

const Section = ({ title, children }: { title: string, children: React.ReactNode }) => (
    <Stack gap="8px">
        <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>{title}</div>
        {children}
    </Stack>
);

const Divider = () => <div style={{ height: '1px', backgroundColor: theme.border.default, width: '100%' }} />;
