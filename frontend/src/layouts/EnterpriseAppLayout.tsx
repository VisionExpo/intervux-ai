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
import { roleNavigation, type AppRole } from "./enterpriseNav";

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
    <div className="min-h-screen bg-[#f7f9fb]">
      <aside className="hidden h-screen w-72 shrink-0 bg-[#f2f4f6] px-6 py-7 md:fixed md:flex md:flex-col">
        <Link to="/" className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-[#004ac6] to-[#2563eb] text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="font-[Manrope] text-lg font-bold text-slate-900">Intervux AI</p>
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-500">Intelligent Layer</p>
          </div>
        </Link>

        <nav className="space-y-1.5">
          {navItems.map((item) => {
            const Icon = iconMap[item.icon as keyof typeof iconMap] || Sparkles;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `group flex items-center justify-between rounded-2xl px-3 py-2.5 text-sm font-medium transition ${
                    isActive ? "bg-white text-[#004ac6] shadow-sm" : "text-slate-600 hover:bg-white/70"
                  }`
                }
              >
                <span className="flex items-center gap-2.5">
                  <Icon className="h-4 w-4" />
                  {item.label}
                </span>
                {item.badge ? <span className="rounded-full bg-[#004ac6] px-2 py-0.5 text-[10px] text-white">{item.badge}</span> : null}
              </NavLink>
            );
          })}
        </nav>

        <div className="mt-auto rounded-3xl bg-white p-4 shadow-[0_16px_32px_-28px_rgba(15,23,42,0.45)]">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Signed in</p>
          <p className="mt-2 text-sm font-semibold text-slate-900">{user?.name || "Intervux User"}</p>
          <p className="text-xs text-slate-500">{user?.email}</p>
          <button
            onClick={handleLogout}
            className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#f2f4f6] px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-[#e6e8ea]"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      <AnimatePresence>
        {menuOpen ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm md:hidden"
            onClick={() => setMenuOpen(false)}
          >
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", damping: 26, stiffness: 230 }}
              className="h-full w-72 bg-[#f2f4f6] p-5"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="mb-6 flex items-center justify-between">
                <p className="font-semibold text-slate-900">Intervux AI</p>
                <button onClick={() => setMenuOpen(false)}>
                  <X className="h-5 w-5 text-slate-700" />
                </button>
              </div>
              <nav className="space-y-1.5">
                {navItems.map((item) => {
                  const Icon = iconMap[item.icon as keyof typeof iconMap] || Sparkles;
                  return (
                    <NavLink
                      key={`mobile-${item.path}`}
                      to={item.path}
                      onClick={() => setMenuOpen(false)}
                      className={({ isActive }) => `flex items-center gap-2.5 rounded-2xl px-3 py-2.5 text-sm ${isActive ? "bg-white text-[#004ac6]" : "text-slate-600"}`}
                    >
                      <Icon className="h-4 w-4" />
                      {item.label}
                    </NavLink>
                  );
                })}
              </nav>
            </motion.aside>
          </motion.div>
        ) : null}
      </AnimatePresence>

      <div className="md:ml-72">
        <header className="sticky top-0 z-30 bg-[#f7f9fb]/90 px-4 py-3 backdrop-blur md:px-8">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <button className="rounded-xl bg-white p-2 text-slate-700 md:hidden" onClick={() => setMenuOpen(true)} aria-label="Open navigation">
                <Menu className="h-4 w-4" />
              </button>
              <div>
                <p className="text-xs uppercase tracking-[0.14em] text-slate-500">Workspace</p>
                <p className="font-[Manrope] text-base font-semibold text-slate-900">{location.pathname}</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="hidden items-center gap-2 rounded-xl bg-white px-3 py-2 md:flex">
                <Search className="h-4 w-4 text-slate-400" />
                <input className="w-56 bg-transparent text-sm text-slate-700 outline-none" placeholder="Search candidates, jobs, reports" readOnly />
              </div>
              <button className="rounded-xl bg-white p-2 text-slate-600">
                <Bell className="h-4 w-4" />
              </button>
            </div>
          </div>
        </header>

        <main className="px-4 py-6 md:px-8">{children}</main>
      </div>
    </div>
  );
}
