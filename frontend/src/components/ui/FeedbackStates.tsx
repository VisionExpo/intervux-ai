import React from "react";
import { AlertCircle, RotateCcw } from "lucide-react";
import { Button } from "./Button/Button";
import { SurfaceCard } from "./SurfaceCard";

interface DashboardErrorProps {
  message: string;
  onRetry: () => void;
}

export function DashboardError({ message, onRetry }: DashboardErrorProps) {
  return (
    <SurfaceCard className="flex flex-col items-center justify-center p-12 text-center border-rose-500/20 glass-heavy">
      <div className="p-4 rounded-full bg-rose-500/10 text-rose-500 mb-6 animate-pulse">
        <AlertCircle size={48} />
      </div>
      <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">Systems Connection Error</h3>
      <p className="text-[var(--text-secondary)] max-w-sm mb-8">
        We encountered a synchronization issue while fetching your telemetry: <br />
        <span className="text-rose-400 font-mono text-sm">{message}</span>
      </p>
      <Button onClick={onRetry} variant="secondary" className="gap-2">
        <RotateCcw size={16} />
        Initialize Data Retry
      </Button>
    </SurfaceCard>
  );
}

interface EmptyStateProps {
  title: string;
  description: string;
  icon: React.ElementType<{ size?: number; className?: string }>;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ title, description, icon: Icon, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-[var(--border-glass)] rounded-[var(--radius-lg)] bg-[var(--surface-glass-light)]">
      <div className="p-4 rounded-2xl bg-[var(--surface-glass-heavy)] text-[var(--text-secondary)] mb-6 opacity-40">
        <Icon size={40} />
      </div>
      <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">{title}</h3>
      <p className="text-sm text-[var(--text-secondary)] max-w-xs mb-8">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="secondary">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
