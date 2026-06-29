import { AppShell } from '../../design-system/components/primitives';
import { theme } from '../../design-system/tokens/theme';

interface DashboardShellProps {
    topRegion?: React.ReactNode;
    leftRegion?: React.ReactNode;
    workspaceRegion?: React.ReactNode;
    rightRegion?: React.ReactNode;
    bottomRegion?: React.ReactNode;
}

export const DashboardShell = ({
    topRegion,
    leftRegion,
    workspaceRegion,
    rightRegion,
    bottomRegion
}: DashboardShellProps) => {
    return (
        <AppShell>
            {/* Top Region */}
            {topRegion && (
                <div style={{ flexShrink: 0, height: '60px', backgroundColor: theme.surface.elevated, borderBottom: `1px solid ${theme.border.default}` }}>
                    {topRegion}
                </div>
            )}

            {/* Main Layout Area */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                {/* Left Region */}
                {leftRegion && (
                    <div style={{ width: '280px', flexShrink: 0, borderRight: `1px solid ${theme.border.default}`, backgroundColor: theme.sidebar.background, display: 'flex', flexDirection: 'column' }}>
                        {leftRegion}
                    </div>
                )}

                {/* Workspace Region (Center) */}
                <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', backgroundColor: theme.workspace.background }}>
                    {workspaceRegion}
                </div>

                {/* Right Region */}
                {rightRegion && (
                    <div style={{ width: '300px', flexShrink: 0, borderLeft: `1px solid ${theme.border.default}`, backgroundColor: theme.sidebar.background, display: 'flex', flexDirection: 'column' }}>
                        {rightRegion}
                    </div>
                )}
            </div>

            {/* Bottom Region */}
            {bottomRegion && (
                <div style={{ flexShrink: 0, height: '40px', backgroundColor: theme.surface.elevated, borderTop: `1px solid ${theme.border.default}` }}>
                    {bottomRegion}
                </div>
            )}
        </AppShell>
    );
};
