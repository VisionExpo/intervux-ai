import { AppShell, Card, Panel, Stack, Toolbar, StatusBar } from '../design-system/components/primitives';
import { theme } from '../design-system/tokens/theme';
import '../design-system/animations/motion.css';

export const ComponentPreview = () => (
    <AppShell className="component-preview">
        <Toolbar>
            <div style={{ fontWeight: 600 }}>Design System: Living Reference</div>
        </Toolbar>
        
        <div style={{ flex: 1, overflowY: 'auto', padding: '48px', display: 'flex', flexDirection: 'column', gap: '48px' }}>
            
            <section>
                <h2 style={{ marginBottom: '24px', color: theme.text.secondary }}>Colors</h2>
                <Stack direction="row" gap="16px">
                    <ColorSwatch label="Surface Default" color={theme.surface.default} />
                    <ColorSwatch label="Surface Elevated" color={theme.surface.elevated} />
                    <ColorSwatch label="Brand Primary" color={theme.brand.primary} />
                    <ColorSwatch label="Success" color={theme.status.success} />
                    <ColorSwatch label="Warning" color={theme.status.warning} />
                    <ColorSwatch label="Error" color={theme.status.error} />
                </Stack>
            </section>

            <section>
                <h2 style={{ marginBottom: '24px', color: theme.text.secondary }}>Primitives</h2>
                <Stack direction="row" gap="24px">
                    <Card padding="24px" style={{ width: '300px' }}>
                        <h3 style={{ margin: '0 0 16px 0' }}>Card Component</h3>
                        <p style={{ color: theme.text.muted, margin: 0 }}>This is a card with standard padding and borders.</p>
                    </Card>
                    <Panel style={{ width: '300px', padding: '24px' }}>
                        <h3 style={{ margin: '0 0 16px 0' }}>Panel Component</h3>
                        <p style={{ color: theme.text.muted, margin: 0 }}>Panels are used for larger workspace areas.</p>
                    </Panel>
                </Stack>
            </section>

            <section>
                <h2 style={{ marginBottom: '24px', color: theme.text.secondary }}>Motion</h2>
                <Stack direction="row" gap="48px">
                    <div className="motion-thinking" style={{ padding: '24px', background: theme.surface.elevated, borderRadius: theme.radius.md, border: `1px solid ${theme.interview.ai}` }}>
                        Thinking (Pulse Glow)
                    </div>
                    <div className="motion-recording" style={{ padding: '24px', background: theme.surface.elevated, borderRadius: theme.radius.md, color: theme.status.error, fontWeight: 'bold' }}>
                        Recording (Fade Pulse)
                    </div>
                    <div className="motion-loading" style={{ padding: '24px', background: theme.surface.elevated, borderRadius: theme.radius.full }}>
                        ⚙️
                    </div>
                </Stack>
            </section>

        </div>
        <StatusBar>Intervux OS Component Library</StatusBar>
    </AppShell>
);

const ColorSwatch = ({ label, color }: { label: string, color: string }) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <div style={{ width: '100px', height: '100px', backgroundColor: color, borderRadius: theme.radius.md, border: `1px solid ${theme.border.default}` }} />
        <div style={{ fontSize: '0.75rem', color: theme.text.muted, width: '100px', wordWrap: 'break-word' }}>{label}</div>
    </div>
);
