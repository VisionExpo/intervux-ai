import Sidebar from './Sidebar';

interface AppShellProps {
  children: React.ReactNode;
  currentPath: string;
}

export default function AppShell({ children, currentPath }: AppShellProps) {
  return (
    <div className="app-shell">
      <Sidebar currentPath={currentPath} />
      <main className="app-main">
        <div className="app-main-inner">
          {children}
        </div>
      </main>
    </div>
  );
}
