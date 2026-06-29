// ============================================================================
// Design Tokens
//
// Do not use hardcoded colors or spacing in components. Always use these tokens.
// ============================================================================

export const colors = {
    // Surface
    surface: 'var(--color-surface, #09090b)', // default dark zinc-950
    surfaceElevated: 'var(--color-surface-elevated, #18181b)', // zinc-900
    workspace: 'var(--color-workspace, #121214)',
    sidebar: 'var(--color-sidebar, #09090b)',
    card: 'var(--color-card, #18181b)',
    
    // Border
    border: 'var(--color-border, #27272a)', // zinc-800
    borderFocus: 'var(--color-border-focus, #3b82f6)', // blue-500
    
    // Brand/Semantic
    primary: 'var(--color-primary, #3b82f6)',
    primaryHover: 'var(--color-primary-hover, #2563eb)',
    success: 'var(--color-success, #22c55e)', // emerald-500
    warning: 'var(--color-warning, #eab308)', // yellow-500
    danger: 'var(--color-danger, #ef4444)',   // red-500
    
    // Text
    textPrimary: 'var(--color-text-primary, #f8fafc)', // slate-50
    textSecondary: 'var(--color-text-secondary, #94a3b8)', // slate-400
    textMuted: 'var(--color-text-muted, #64748b)', // slate-500
};

export const spacing = {
    4: '0.25rem',
    8: '0.5rem',
    12: '0.75rem',
    16: '1rem',
    24: '1.5rem',
    32: '2rem',
    48: '3rem',
    64: '4rem',
};

export const radius = {
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    full: '9999px',
};

export const shadows = {
    panel: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    floating: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    modal: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
};

export const motion = {
    fast: '150ms ease-in-out',
    normal: '300ms ease-in-out',
    slow: '500ms ease-in-out',
};

export const theme = {
    colors,
    spacing,
    radius,
    shadows,
    motion
};
