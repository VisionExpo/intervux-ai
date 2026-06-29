import { Card, Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

export const VoiceControlPanel = () => (
    <Card className="voice-control-panel" padding="16px">
        <Stack gap="16px">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: theme.status.success }}>
                    <span className="motion-recording">🎤</span>
                    <span style={{ fontWeight: 600 }}>Recording</span>
                </div>
                <div style={{ color: theme.text.secondary, fontSize: '0.875rem' }}>
                    00:37
                </div>
            </div>
            
            {/* Visualizer Placeholder */}
            <div style={{ height: '24px', display: 'flex', gap: '4px', alignItems: 'center' }}>
                {Array.from({ length: 20 }).map((_, i) => (
                    <div key={i} style={{ 
                        flex: 1, 
                        height: i % 2 === 0 ? '100%' : '60%', 
                        backgroundColor: i < 12 ? theme.status.success : theme.border.default, 
                        borderRadius: '2px' 
                    }} />
                ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
                <button style={{ 
                    padding: '8px 24px', 
                    backgroundColor: theme.brand.primary, 
                    color: '#fff', 
                    border: 'none', 
                    borderRadius: theme.radius.md, 
                    cursor: 'pointer',
                    fontWeight: 600
                }}>
                    Done Speaking
                </button>
            </div>
        </Stack>
    </Card>
);
