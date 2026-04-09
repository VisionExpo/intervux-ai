import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';

interface AppShellProps {
  children: React.ReactNode;
  currentPath: string;
}

export default function AppShell({ children, currentPath }: AppShellProps) {
  return (
    <div className="min-h-screen bg-surface font-body text-on-surface flex">
      <Sidebar currentPath={currentPath} />
      <main className="ml-64 flex-1 flex flex-col min-h-screen relative w-[calc(100%-16rem)]">
        <DashboardHeader />
        <div className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
