export function DashboardSkeleton() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
        {Array.from({ length: 4 }).map((_, index) => (
          <div 
            key={index} 
            style={{ 
              height: '8rem', 
              borderRadius: 'var(--radius-lg)', 
              border: '1px solid var(--border-glass)', 
              background: 'var(--surface-glass-light)', 
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' 
            }} 
          />
        ))}
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
        <div 
          style={{ 
            height: '18rem', 
            borderRadius: 'var(--radius-lg)', 
            border: '1px solid var(--border-glass)', 
            background: 'var(--surface-glass-light)', 
            animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            gridColumn: '1 / -1' 
          }} 
        />
      </div>
    </div>
  );
}
