import { Card, Stack } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

interface VoiceControlProps {
    isListening: boolean;
    onDoneSpeaking?: () => void;
}

export const VoiceControlPanel = ({ isListening, onDoneSpeaking }: VoiceControlProps) => (
    <Card className="voice-control-panel" padding="16px">
        <Stack gap="16px">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: isListening ? theme.status.success : theme.text.muted }}>
                    <span className={isListening ? "motion-recording" : ""}>🎤</span>
                    <span style={{ fontWeight: 600 }}>{isListening ? 'Recording' : 'Listening'}</span>
                </div>
                <div style={{ color: theme.text.secondary, fontSize: '0.875rem' }}>
                    --:--
                </div>
            </div>
            
            {/* Visualizer Placeholder */}
            <div style={{ height: '24px', display: 'flex', gap: '4px', alignItems: 'center', opacity: isListening ? 1 : 0.3 }}>
                {Array.from({ length: 20 }).map((_, i) => (
                    <div key={i} style={{ 
                        flex: 1, 
                        height: i % 2 === 0 ? '100%' : '60%', 
                        backgroundColor: i < 12 ? (isListening ? theme.status.success : theme.text.muted) : theme.border.default, 
                        borderRadius: '2px' 
                    }} />
                ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'center' }}>
                <button 
                    onClick={onDoneSpeaking}
                    disabled={!isListening}
                    style={{ 
                        padding: '8px 24px', 
                        backgroundColor: isListening ? theme.brand.primary : theme.border.default, 
                        color: isListening ? '#fff' : theme.text.muted, 
                        border: 'none', 
                        borderRadius: theme.radius.md, 
                        cursor: isListening ? 'pointer' : 'not-allowed',
                        fontWeight: 600
                    }}
                >
                    Done Speaking
                </button>
            </div>
        </Stack>
    </Card>
);
