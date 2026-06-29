// ============================================================================
// Semantic Theme Tokens
// ============================================================================

export const theme = {
    surface: {
        default: 'var(--theme-surface-default, #09090b)',
        elevated: 'var(--theme-surface-elevated, #18181b)',
        overlay: 'var(--theme-surface-overlay, rgba(9, 9, 11, 0.8))',
    },
    workspace: {
        background: 'var(--theme-workspace-bg, #121214)',
        panel: 'var(--theme-workspace-panel, #18181b)',
    },
    sidebar: {
        background: 'var(--theme-sidebar-bg, #09090b)',
        hover: 'var(--theme-sidebar-hover, #27272a)',
    },
    card: {
        background: 'var(--theme-card-bg, #18181b)',
        border: 'var(--theme-card-border, #27272a)',
    },
    border: {
        default: 'var(--theme-border-default, #27272a)',
        focus: 'var(--theme-border-focus, #3b82f6)',
    },
    text: {
        primary: 'var(--theme-text-primary, #f8fafc)',
        secondary: 'var(--theme-text-secondary, #94a3b8)',
        muted: 'var(--theme-text-muted, #64748b)',
        inverse: 'var(--theme-text-inverse, #0f172a)',
    },
    brand: {
        primary: 'var(--theme-brand-primary, #3b82f6)',
        primaryHover: 'var(--theme-brand-primary-hover, #2563eb)',
    },
    radius: {
        sm: '0.125rem',
        md: '0.375rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
    },
    status: {
        success: 'var(--theme-status-success, #22c55e)',
        warning: 'var(--theme-status-warning, #eab308)',
        error: 'var(--theme-status-error, #ef4444)',
        info: 'var(--theme-status-info, #3b82f6)',
    },
    interview: {
        ai: 'var(--theme-interview-ai, #8b5cf6)', // Purple for AI
        candidate: 'var(--theme-interview-candidate, #3b82f6)', // Blue for Candidate
    }
} as const;

export type Theme = typeof theme;
