import { theme } from '../../design-system/tokens/theme';

export const InterviewerView = ({ children }: { children: React.ReactNode }) => (
    <div style={{ 
        flex: 1, 
        backgroundColor: theme.surface.elevated, 
        borderRadius: theme.radius.md, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        border: `1px solid ${theme.border.default}`, 
        position: 'relative', 
        overflow: 'hidden',
        minHeight: '300px'
    }}>
        {children}
    </div>
);
