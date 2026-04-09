export type Role = 'candidate' | 'recruiter' | 'admin';

export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
}

export interface NavSection {
  title?: string;
  items: NavItem[];
}

export const ROLE_NAVIGATION: Record<Role, NavSection[]> = {
  candidate: [
    {
      items: [
        { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
        { id: 'profile', label: 'Profile Settings', path: '/profile', icon: 'person' },
        { id: 'mock-interview', label: 'Mock Interview', path: '/mock-interview', icon: 'psychology' },
        { id: 'interview-history', label: 'History', path: '/interview-history', icon: 'history' },
        { id: 'notifications', label: 'Notifications', path: '/notifications', icon: 'notifications' },
      ],
    },
  ],
  recruiter: [
    {
      items: [
        { id: 'dashboard', label: 'Dashboard', path: '/dashboard', icon: 'dashboard' },
        { id: 'candidates', label: 'Candidates', path: '/candidates', icon: 'group' },
        { id: 'interviews', label: 'Interviews', path: '/interviews', icon: 'event_available' },
        { id: 'analytics', label: 'Analytics', path: '/analytics', icon: 'insights' },
      ],
    },
  ],
  admin: [
    {
      items: [
        { id: 'dashboard', label: 'Global Metrics', path: '/dashboard', icon: 'dashboard' },
        { id: 'users', label: 'User Management', path: '/users', icon: 'group' },
        { id: 'experiments', label: 'Experiments', path: '/experiments', icon: 'science' },
        { id: 'evaluation', label: 'Evaluation Dashboard', path: '/evaluation', icon: 'analytics' },
        { id: 'system-health', label: 'System Health', path: '/system-health', icon: 'monitor_heart' },
        { id: 'settings', label: 'Platform Settings', path: '/settings', icon: 'settings' },
        { id: 'audit-logs', label: 'Audit Logs', path: '/audit-logs', icon: 'history' },
      ],
    },
  ],
};
