
import { Panel, Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';
import { isFeatureEnabled } from '../../core/state/features';

export const CandidateMonitor = ({ children }: { children?: React.ReactNode }) => (
    <Panel className="candidate-monitor" style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <div style={{ 
            position: 'absolute', 
            top: '16px', left: '16px', 
            padding: '4px 8px', 
            backgroundColor: theme.surface.overlay, 
            borderRadius: theme.radius.sm,
            color: theme.text.primary,
            fontSize: '0.875rem',
            zIndex: 10
        }}>
            Candidate Camera
        </div>

        {/* Camera Feed Container */}
        <div style={{ width: '100%', height: '100%', backgroundColor: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
            {children || <span style={{ color: theme.text.muted }}>[ Camera Feed ]</span>}
        </div>

        {/* Vision Analytics Overlay (Future) */}
        {isFeatureEnabled('vision') && (
            <div style={{ position: 'absolute', right: '16px', top: '16px', bottom: '16px', width: '120px' }}>
                <Stack gap="8px">
                    <StatusBadge label="Eye Contact" status="success" />
                    <StatusBadge label="Face" status="success" />
                    <StatusBadge label="Lighting" status="success" />
                    <StatusBadge label="Audio" status="success" />
                    <StatusBadge label="Connection" status="warning" />
                </Stack>
            </div>
        )}
    </Panel>
);

const StatusBadge = ({ label, status }: { label: string; status: 'success' | 'warning' | 'error' }) => (
    <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '6px', 
        padding: '6px', 
        backgroundColor: theme.surface.overlay, 
        borderRadius: theme.radius.sm,
        fontSize: '0.75rem'
    }}>
        <div style={{ 
            width: '8px', height: '8px', borderRadius: '50%', 
            backgroundColor: theme.status[status] 
        }} />
        <span style={{ color: theme.text.secondary }}>{label}</span>
    </div>
);
