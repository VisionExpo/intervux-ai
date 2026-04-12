import React, { useState } from 'react';
import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';

interface AppShellProps {
  children: React.ReactNode;
  currentPath: string;
}

export default function AppShell({ children, currentPath }: AppShellProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="h-screen bg-surface font-body text-on-surface flex overflow-hidden relative">
      <Sidebar currentPath={currentPath} isOpen={isSidebarOpen} />
      
      {/* Mobile Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-30 lg:hidden backdrop-blur-sm animate-in fade-in duration-300"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      <main className="flex-1 flex flex-col relative overflow-y-auto w-full">
        <DashboardHeader onMenuOpen={() => setIsSidebarOpen(true)} />
        <div className="flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
