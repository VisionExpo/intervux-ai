import { useMemo, useState, type ReactNode } from "react";
import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  Bell,
  BriefcaseBusiness,
  CalendarCheck2,
  ChartColumn,
  ClipboardList,
  FlaskConical,
  LayoutDashboard,
  LineChart,
  Menu,
  Mic2,
  Search,
  ShieldCheck,
  Sparkles,
  UserRound,
  Users,
  X,
  LogOut,
} from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import styles from "./EnterpriseAppLayout.module.css";

/* ── Navigation config (inlined from removed enterpriseNav.ts) ── */
type AppRole = "candidate" | "recruiter" | "admin";

interface NavItem {
  label: string;
  path: string;
  icon: string;
  badge?: string;
}

const roleNavigation: Record<AppRole, NavItem[]> = {
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

const iconMap = {
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

interface EnterpriseAppLayoutProps {
  children: ReactNode;
}

export function EnterpriseAppLayout({ children }: EnterpriseAppLayoutProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const role = ((user?.role as AppRole) || "candidate") as AppRole;
  const navItems = useMemo(() => roleNavigation[role] || roleNavigation.candidate, [role]);

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <div className={styles.appLayout}>
      {/* Desktop Sidebar */}
      <aside className={styles.sidebar}>
        <Link to="/" className={styles.brandLink}>
          <div className={styles.brandIcon}>
            <Sparkles size={18} />
          </div>
          <div>
            <p className={styles.brandText}>Intervux AI</p>
            <p className={styles.brandSubtext}>Intelligent Layer</p>
          </div>
        </Link>

        <nav className={styles.navContainer}>
          {navItems.map((item) => {
            const Icon = iconMap[item.icon as keyof typeof iconMap] || Sparkles;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `${styles.navItem} ${isActive ? styles.navItemActive : ""}`
                }
              >
                <span>
                  <Icon size={16} />
                  {item.label}
                </span>
                {item.badge ? <span className={styles.navBadge}>{item.badge}</span> : null}
              </NavLink>
            );
          })}
        </nav>

        <div className={styles.userProfile}>
          <p className={styles.userProfileLabel}>Signed in</p>
          <p className={styles.userName}>{user?.name || "Intervux User"}</p>
          <p className={styles.userEmail}>{user?.email}</p>
          <button onClick={handleLogout} className={styles.logoutBtn}>
            <LogOut size={14} />
            Logout
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {menuOpen ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className={styles.mobileOverlay}
            onClick={() => setMenuOpen(false)}
          >
            <motion.aside
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", damping: 26, stiffness: 230 }}
              className={styles.mobileSidebar}
              onClick={(event) => event.stopPropagation()}
            >
              <div className={styles.mobileHeader}>
                <span>Intervux AI</span>
                <button className={styles.mobileClose} onClick={() => setMenuOpen(false)}>
                  <X size={20} />
                </button>
              </div>
              <nav className={styles.navContainer}>
                {navItems.map((item) => {
                  const Icon = iconMap[item.icon as keyof typeof iconMap] || Sparkles;
                  return (
                    <NavLink
                      key={`mobile-${item.path}`}
                      to={item.path}
                      onClick={() => setMenuOpen(false)}
                      className={({ isActive }) =>
                        `${styles.navItem} ${isActive ? styles.navItemActive : ""}`
                      }
                    >
                      <span>
                        <Icon size={16} />
                        {item.label}
                      </span>
                    </NavLink>
                  );
                })}
              </nav>
              <button onClick={handleLogout} className={styles.logoutBtn} style={{ marginTop: "auto" }}>
                <LogOut size={14} />
                Logout
              </button>
            </motion.aside>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {/* Main Content */}
      <div className={styles.mainWrapper}>
        <header className={styles.topHeader}>
          <div className={styles.headerLeft}>
            <button className={styles.mobileMenuBtn} onClick={() => setMenuOpen(true)} aria-label="Open navigation">
              <Menu size={16} />
            </button>
            <div className={styles.pageContext}>
              <p className={styles.pageContextLabel}>Workspace</p>
              <p className={styles.pageContextTitle}>{location.pathname}</p>
            </div>
          </div>

          <div className={styles.headerRight}>
            <div className={styles.searchBox}>
              <Search size={14} color="var(--text-secondary)" />
              <input className={styles.searchInput} placeholder="Search candidates, jobs, reports" readOnly />
            </div>
            <button className={styles.iconBtn}>
              <Bell size={16} />
            </button>
          </div>
        </header>

        <main className={styles.contentArea}>{children}</main>
      </div>
    </div>
  );
}
