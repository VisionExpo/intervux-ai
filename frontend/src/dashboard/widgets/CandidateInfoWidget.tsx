import { Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

export interface CandidateInfoProps {
    candidateName?: string;
    role?: string;
    skills?: string[];
    isUploadingResume?: boolean;
    onUploadResume?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    needsResume?: boolean;
}

export const CandidateInfoWidget = ({ candidateName, role, skills, isUploadingResume, onUploadResume, needsResume }: CandidateInfoProps) => (
    <Stack gap="16px" className="candidate-info-widget" style={{ padding: '24px' }}>
        <div style={{ color: theme.text.muted, fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Candidate Profile</div>
        {needsResume ? (
            <div style={{ 
                border: `1px dashed ${theme.border.default}`, 
                borderRadius: theme.radius.md, 
                padding: '24px', 
                textAlign: 'center',
                backgroundColor: theme.surface.elevated
            }}>
                <div style={{ marginBottom: '12px', fontSize: '2rem' }}>
                    {isUploadingResume ? "⏳" : "📄"}
                </div>
                <div style={{ color: theme.text.primary, fontWeight: 600, marginBottom: '8px' }}>
                    {isUploadingResume ? "Processing Resume" : "Upload Resume"}
                </div>
                {!isUploadingResume && onUploadResume && (
                    <label style={{ 
                        display: 'inline-block',
                        padding: '8px 16px', 
                        backgroundColor: theme.surface.default, 
                        border: `1px solid ${theme.border.default}`,
                        borderRadius: theme.radius.md,
                        cursor: 'pointer',
                        fontSize: '0.875rem',
                        fontWeight: 500,
                        color: theme.text.primary
                    }}>
                        Select File
                        <input type="file" accept=".pdf,.doc,.docx" onChange={onUploadResume} style={{ display: 'none' }} />
                    </label>
                )}
            </div>
        ) : (
            <Stack gap="12px">
                <div>
                    <div style={{ fontWeight: 600, color: theme.text.primary, fontSize: '1.125rem' }}>{candidateName || "Anonymous Candidate"}</div>
                    <div style={{ color: theme.text.secondary, fontSize: '0.875rem' }}>{role || "Unknown Role"}</div>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {skills?.map(skill => (
                        <div key={skill} style={{ padding: '4px 8px', backgroundColor: theme.surface.elevated, borderRadius: theme.radius.sm, fontSize: '0.75rem', color: theme.text.secondary }}>
                            {skill}
                        </div>
                    ))}
                </div>
            </Stack>
        )}
    </Stack>
);
