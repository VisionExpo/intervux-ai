import { useAuth } from '../hooks/useAuth';

const navItems = [
  { path: '/dashboard',         label: 'Dashboard',        icon: '⚡' },
  { path: '/profile',           label: 'My Profile',       icon: '👤' },
  { path: '/mock-interview',    label: 'Mock Interview',   icon: '🎙️' },
  { path: '/interview-history', label: 'History',          icon: '📋' },
  { path: '/notifications',     label: 'Notifications',    icon: '🔔' },
];

interface SidebarProps {
  currentPath: string;
}

export default function Sidebar({ currentPath }: SidebarProps) {
  const { user } = useAuth();
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
    : 'U';

  return (
    <aside className="app-sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="sidebar-logo-mark">
          <span>⚡</span>
        </div>
        <span className="sidebar-brand-name">Intervux<span className="sidebar-brand-accent"> AI</span></span>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        <p className="sidebar-nav-label-group">Menu</p>
        {navItems.map(item => {
          const isActive = currentPath === item.path;
          return (
            <a
              key={item.path}
              href={`#${item.path}`}
              className={`sidebar-nav-item${isActive ? ' active' : ''}`}
            >
              <span className="sidebar-nav-icon">{item.icon}</span>
              <span className="sidebar-nav-text">{item.label}</span>
              {isActive && <span className="sidebar-active-dot" />}
            </a>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">{initials}</div>
          <div className="sidebar-user-info">
            <p className="sidebar-user-name">{user?.name || 'Candidate'}</p>
            <p className="sidebar-user-role">Candidate</p>
          </div>
        </div>
        <a href="#/logout" className="sidebar-logout-btn">
          <span>↩</span>
          <span>Logout</span>
        </a>
      </div>
    </aside>
  );
}
