import React from 'react';
import { theme } from '../tokens/theme';

// ============================================================================
// Layout Primitives
// Extremely generic building blocks for the Interview Dashboard
// ============================================================================

export const AppShell = ({ children, className = '', style = {} }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) => (
    <div className={`app-shell ${className}`} style={{ backgroundColor: theme.surface.default, color: theme.text.primary, height: '100vh', width: '100vw', display: 'flex', flexDirection: 'column', overflow: 'hidden', ...style }}>
        {children}
    </div>
);

export const Workspace = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
    <div className={`workspace ${className}`} style={{ flex: 1, display: 'flex', backgroundColor: theme.workspace.background, position: 'relative', overflow: 'hidden' }}>
        {children}
    </div>
);

export const Sidebar = ({ children, width = '250px', className = '' }: { children: React.ReactNode; width?: string; className?: string }) => (
    <aside className={`sidebar ${className}`} style={{ width, backgroundColor: theme.sidebar.background, borderRight: `1px solid ${theme.border.default}`, display: 'flex', flexDirection: 'column' }}>
        {children}
    </aside>
);

export const Panel = ({ children, className = '', style = {} }: { children: React.ReactNode; className?: string; style?: React.CSSProperties }) => (
    <div className={`panel ${className}`} style={{ backgroundColor: theme.workspace.panel, borderRadius: '8px', border: `1px solid ${theme.border.default}`, display: 'flex', flexDirection: 'column', ...style }}>
        {children}
    </div>
);

export const Card = ({ children, padding = '16px', className = '', style = {} }: { children: React.ReactNode; padding?: string; className?: string; style?: React.CSSProperties }) => (
    <div className={`card ${className}`} style={{ backgroundColor: theme.card.background, border: `1px solid ${theme.card.border}`, borderRadius: '6px', padding, ...style }}>
        {children}
    </div>
);

export const Stack = ({ children, gap = '16px', direction = 'column', className = '', style = {} }: { children: React.ReactNode; gap?: string; direction?: 'column' | 'row'; className?: string; style?: React.CSSProperties }) => (
    <div className={`stack ${className}`} style={{ display: 'flex', flexDirection: direction, gap, ...style }}>
        {children}
    </div>
);

export const SplitView = ({ left, right, leftWidth = '50%' }: { left: React.ReactNode; right: React.ReactNode; leftWidth?: string }) => (
    <div style={{ display: 'flex', width: '100%', height: '100%' }}>
        <div style={{ width: leftWidth, height: '100%' }}>{left}</div>
        <div style={{ flex: 1, height: '100%' }}>{right}</div>
    </div>
);

export const Toolbar = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
    <div className={`toolbar ${className}`} style={{ display: 'flex', alignItems: 'center', padding: '8px 16px', borderBottom: `1px solid ${theme.border.default}`, backgroundColor: theme.surface.elevated }}>
        {children}
    </div>
);

export const StatusBar = ({ children, className = '' }: { children: React.ReactNode; className?: string }) => (
    <div className={`status-bar ${className}`} style={{ height: '32px', display: 'flex', alignItems: 'center', padding: '0 16px', borderTop: `1px solid ${theme.border.default}`, backgroundColor: theme.surface.elevated, fontSize: '0.75rem', color: theme.text.secondary }}>
        {children}
    </div>
);

export const Overlay = ({ children, isVisible }: { children: React.ReactNode; isVisible: boolean }) => {
    if (!isVisible) return null;
    return (
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: theme.surface.overlay, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
            {children}
        </div>
    );
};
