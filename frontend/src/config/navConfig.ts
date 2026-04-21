import { 
  Bell, 
  BriefcaseBusiness, 
  CalendarCheck2, 
  ChartColumn, 
  ClipboardList, 
  FlaskConical, 
  LayoutDashboard, 
  LineChart, 
  Mic2, 
  ShieldCheck, 
  Sparkles, 
  UserRound, 
  Users 
} from "lucide-react";

export type AppRole = "candidate" | "recruiter" | "admin";

export interface NavItem {
  label: string;
  path: string;
  icon: keyof typeof iconMap;
  badge?: string;
}

export const iconMap = {
  sparkles: Sparkles,
  "mic-2": Mic2,
  "file-chart-column": ChartColumn,
  "user-round": UserRound,
  bell: Bell,
  "briefcase-business": BriefcaseBusiness,
  "chart-column": ChartColumn,
  users: Users,
  "calendar-check-2": CalendarCheck2,
  "layout-dashboard": LayoutDashboard,
  "shield-check": ShieldCheck,
  "line-chart": LineChart,
  "clipboard-list": ClipboardList,
  "flask-conical": FlaskConical,
} as const;

export const roleNavigation: Record<AppRole, NavItem[]> = {
  candidate: [
    { label: "Intelligence", path: "/candidate", icon: "sparkles" },
    { label: "Interviews", path: "/interviews", icon: "mic-2" },
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
