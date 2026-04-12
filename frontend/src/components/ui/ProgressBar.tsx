// Imports removed
interface ProgressBarProps {
  label: string;
  value: number;
  helper?: string;
}

export function ProgressBar({ label, value, helper }: ProgressBarProps) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{label}</span>
        <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{value}%</span>
      </div>
      <div style={{ height: '0.5rem', background: 'var(--surface-glass-light)', borderRadius: '999px', overflow: 'hidden' }}>
        <div
          style={{ 
            height: '100%', 
            width: `${Math.max(0, Math.min(100, value))}%`,
            background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-ocean))',
            borderRadius: '999px',
            transition: 'width 0.5s ease-out'
          }}
        />
      </div>
      {helper ? <p style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{helper}</p> : null}
    </div>
  );
}
