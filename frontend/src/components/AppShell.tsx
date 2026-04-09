import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';

interface AppShellProps {
  children: React.ReactNode;
  currentPath: string;
}

export default function AppShell({ children, currentPath }: AppShellProps) {
  return (
    <div className="h-screen bg-surface font-body text-on-surface flex overflow-hidden">
      <Sidebar currentPath={currentPath} />
      <main className="flex-1 flex flex-col relative overflow-y-auto">
        <DashboardHeader />
        <div className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
