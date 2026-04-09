import { useAuth } from '../hooks/useAuth';

export default function DashboardHeader() {
  const { user } = useAuth();
  
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : 'U';
    
  // Dynamic top-left branding based on role
  const roleName = user?.role === 'candidate' ? 'Candidate Dashboard' : 'Intelligence Layer';

  return (
    <header className="w-full sticky top-0 z-30 bg-surface/70 dark:bg-slate-900/70 backdrop-blur-xl flex items-center justify-between px-8 py-4 border-b border-outline-variant/10">
      <div className="flex items-center gap-8">
        <h1 className="text-lg font-bold tracking-tight text-slate-900 dark:text-white font-headline">{roleName}</h1>
        {user?.role !== 'candidate' && (
          <div className="relative hidden md:block">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">search</span>
            <input 
              className="bg-surface-container-low border-none rounded-full py-1.5 pl-10 pr-4 text-sm w-64 focus:ring-2 focus:outline-none focus:ring-primary/20 transition-all text-on-surface" 
              placeholder="Search insights..." 
              type="text"
            />
          </div>
        )}
      </div>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4 text-slate-500">
          <span className="material-symbols-outlined cursor-pointer hover:text-primary transition-colors">notifications</span>
          <span className="material-symbols-outlined cursor-pointer hover:text-primary transition-colors">help</span>
          <span className="material-symbols-outlined cursor-pointer hover:text-primary transition-colors">settings</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-container/20 flex items-center justify-center border border-primary/20">
            <span className="text-primary font-bold text-xs">{initials}</span>
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-semibold text-on-surface">{user?.name || 'User'}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
