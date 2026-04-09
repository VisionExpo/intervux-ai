import React from 'react';

interface DashboardCardProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export const DashboardCard: React.FC<DashboardCardProps> = ({ children, className = '', noPadding = false }) => {
  return (
    <div className={`bg-surface-container-lowest rounded-[1.5rem] shadow-sm border border-white ${noPadding ? '' : 'p-6 lg:p-8'} ${className}`}>
      {children}
    </div>
  );
};
