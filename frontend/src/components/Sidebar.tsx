import { useAuth } from '../hooks/useAuth';
import { ROLE_NAVIGATION, type Role } from '../config/navConfig';

interface SidebarProps {
  currentPath: string;
}

export default function Sidebar({ currentPath }: SidebarProps) {
  const { user } = useAuth();
  
  // Default to candidate if no role or unauthenticated
  const role: Role = (user?.role as Role) || 'candidate';
  const navSections = ROLE_NAVIGATION[role] || ROLE_NAVIGATION['candidate'];

  return (
    <aside className="h-screen w-64 fixed left-0 top-0 bg-surface-container-low dark:bg-slate-950 flex flex-col p-4 gap-2 font-body text-sm font-medium z-40 border-r border-outline-variant/20">
      {/* Brand */}
      <div className="mb-8 px-2 flex items-center gap-3">
        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white">
          <span className="material-symbols-outlined">science</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white leading-tight font-headline">Intervux AI</h2>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold font-headline">{role === 'candidate' ? 'Candidate Portal' : 'Intelligence Layer'}</p>
        </div>
      </div>

      {/* Nav */}
      <div className="flex-1 overflow-y-auto space-y-6">
        {navSections.map((section, idx) => (
          <nav key={idx} className="space-y-1">
            {section.title && (
              <p className="px-3 pb-2 text-xs font-bold uppercase tracking-wider text-slate-400">{section.title}</p>
            )}
            {section.items.map(item => {
              const isActive = currentPath === item.path;
              const linkClasses = isActive
                ? "flex items-center gap-3 px-3 py-2.5 rounded-lg bg-surface-container-lowest dark:bg-slate-900 text-primary dark:text-blue-400 shadow-sm transition-all duration-200 ease-in-out font-semibold"
                : "flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-surface-container-high dark:hover:bg-slate-800 transition-all duration-200 ease-in-out";

              return (
                <a key={item.id} href={`#${item.path}`} className={linkClasses}>
                  <span className="material-symbols-outlined" style={isActive ? {fontVariationSettings: "'FILL' 1"} : {}}>{item.icon}</span>
                  <span>{item.label}</span>
                </a>
              );
            })}
          </nav>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-auto pt-4 space-y-1 border-t border-outline-variant/20">
        {role !== 'candidate' && (
          <button className="w-full mb-4 py-2.5 bg-primary text-white font-semibold rounded-lg shadow-lg shadow-primary/20 active:scale-95 transition-transform">
            New Workspace
          </button>
        )}
        <a className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-surface-container-high transition-all duration-200" href="#">
          <span className="material-symbols-outlined">headset_mic</span>
          <span>Support</span>
        </a>
        <a className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-surface-container-high transition-all duration-200" href="#/logout">
          <span className="material-symbols-outlined text-error">logout</span>
          <span className="text-error">Logout</span>
        </a>
      </div>
    </aside>
  );
}
