import React from 'react';

interface SkeletonProps {
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({ className = "" }) => (
  <div className={`animate-pulse bg-slate-200 dark:bg-slate-700/50 rounded ${className}`} />
);

export const CardSkeleton: React.FC = () => (
  <div className="bg-surface-container-low p-6 rounded-2xl space-y-4">
    <Skeleton className="h-6 w-1/3" />
    <div className="space-y-2">
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/6" />
    </div>
  </div>
);

export const TableSkeleton: React.FC<{ rows?: number }> = ({ rows = 5 }) => (
  <div className="bg-surface-container-low p-6 rounded-2xl space-y-4">
    <Skeleton className="h-6 w-1/4 mb-6" />
    <div className="space-y-4">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="flex-1 space-y-2 py-1">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
          <Skeleton className="h-8 w-16 my-auto" />
        </div>
      ))}
    </div>
  </div>
);

export const KPISkeleton: React.FC = () => (
  <div className="bg-surface-container-low p-6 rounded-2xl flex flex-col justify-between aspect-video">
    <Skeleton className="h-4 w-1/2" />
    <Skeleton className="h-10 w-3/4" />
    <Skeleton className="h-3 w-1/3" />
  </div>
);
