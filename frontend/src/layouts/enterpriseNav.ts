export type AppRole = "candidate" | "recruiter" | "admin";

export interface NavItem {
  label: string;
  path: string;
  icon: string;
  badge?: string;
}

export const roleNavigation: Record<AppRole, NavItem[]> = {
  candidate: [
    { label: "Intelligence", path: "/candidate", icon: "sparkles" },
    { label: "Interviews", path: "/mock-interview", icon: "mic-2" },
    { label: "Reports", path: "/interview-history", icon: "file-chart-column" },
    { label: "Profile", path: "/profile", icon: "user-round" },
    { label: "Notifications", path: "/notifications", icon: "bell" },
  ],
  recruiter: [
    { label: "Recruiter Hub", path: "/recruiter", icon: "briefcase-business" },
    { label: "Analytics", path: "/analytics", icon: "chart-column" },
    { label: "Candidates", path: "/candidates", icon: "users" },
    { label: "Interviews", path: "/interviews", icon: "calendar-check-2" },
  ],
  admin: [
    { label: "Command Center", path: "/admin", icon: "layout-dashboard" },
    { label: "RBAC", path: "/rbac", icon: "shield-check" },
    { label: "Analytics", path: "/analytics", icon: "line-chart" },
    { label: "Audit Logs", path: "/audit-logs", icon: "clipboard-list" },
    { label: "Experiments", path: "/experiments", icon: "flask-conical" },
  ],
};

