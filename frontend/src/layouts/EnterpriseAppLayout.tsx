import { useMemo, useState, type ReactNode } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
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
import { roleNavigation, iconMap, type AppRole } from "../config/navConfig";


interface EnterpriseAppLayoutProps {
  children?: ReactNode;
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
            <div className={`${styles.searchBox} group relative`}>
              <Search size={14} color="var(--text-secondary)" />
              <input className={styles.searchInput} placeholder="Search coming soon..." readOnly />
              <div className="absolute top-full left-0 mt-2 px-2 py-1 bg-[#1e293b] text-[10px] text-white rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-50">
                MVP Search Layer: Currently restricted
              </div>
            </div>
            <button className={styles.iconBtn}>
              <Bell size={16} />
            </button>
          </div>
        </header>

        <main className={styles.contentArea}>{children || <Outlet />}</main>
      </div>
    </div>
  );
}
