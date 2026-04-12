import type { HTMLAttributes } from 'react';
import styles from './GlassCard.module.css';

interface GlassCardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'light' | 'heavy' | 'interactive';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export function GlassCard({ 
  children, 
  variant = 'heavy', 
  padding = 'md',
  className = '', 
  ...props 
}: GlassCardProps) {
  const baseClass = `${styles.card} ${styles[variant]} ${styles[`pad-${padding}`]} ${className}`;

  return (
    <div className={baseClass} {...props}>
      {children}
    </div>
  );
}
