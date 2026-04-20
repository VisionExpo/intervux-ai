import { Suspense, lazy, useEffect, type ReactNode } from "react";
import { HashRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "./hooks/useAuth";
import { EnterpriseAppLayout } from "./layouts/EnterpriseAppLayout";
import { ErrorBoundary } from "./components/ErrorBoundary";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const Login = lazy(() => import("./pages/Login"));
const Signup = lazy(() => import("./pages/Signup"));

const CandidateIntelligencePage = lazy(() => import("./dashboard/CandidateIntelligencePage"));
const RecruiterOperationsPage = lazy(() => import("./dashboard/RecruiterOperationsPage"));
const RecruiterCandidatesPage = lazy(() => import("./recruiter/RecruiterCandidatesPage"));
const RecruiterInterviewsPage = lazy(() => import("./recruiter/RecruiterInterviewsPage"));
const AdminCommandCenterPage = lazy(() => import("./admin/AdminCommandCenterPage"));
const AdminAuditLogsPage = lazy(() => import("./admin/AdminAuditLogsPage"));
const AdminExperimentsPage = lazy(() => import("./admin/AdminExperimentsPage"));
const RbacAccessControlPage = lazy(() => import("./admin/RbacAccessControlPage"));
const AnalyticsIntelligencePage = lazy(() => import("./analytics/AnalyticsIntelligencePage"));

const CandidateProfile = lazy(() => import("./pages/CandidateProfile"));
const MockInterview = lazy(() => import("./pages/MockInterview"));
const InterviewHistory = lazy(() => import("./pages/InterviewHistory"));
const CandidateNotifications = lazy(() => import("./pages/CandidateNotifications"));
const InterviewPage = lazy(() => import("./pages/InterviewPage"));
const CandidateInterviewReport = lazy(() => import("./pages/CandidateInterviewReport"));

function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100">
      <div className="rounded-2xl border border-slate-200 bg-white px-6 py-4 shadow-sm">
        <p className="inline-flex items-center gap-2 text-sm font-semibold text-slate-700">
          <Sparkles className="h-4 w-4 text-blue-600" />
          Loading Intervux AI workspace...
        </p>
      </div>
    </div>
  );
}

function RoleHomeRedirect() {
  const { user } = useAuth();
  if (user?.role === "admin") return <Navigate to="/admin" replace />;
  if (user?.role === "recruiter") return <Navigate to="/recruiter" replace />;
  return <Navigate to="/candidate" replace />;
}

function ProtectedRoute({ children, allowedRoles }: { children: ReactNode; allowedRoles?: string[] }) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (allowedRoles && user?.role && !allowedRoles.includes(user.role)) return <RoleHomeRedirect />;
  return <>{children}</>;
}

function LogoutRoute() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    logout();
    navigate("/", { replace: true });
  }, [logout, navigate]);

  return <LoadingScreen />;
}

function AppContent() {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) return <LoadingScreen />;

  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/" element={isAuthenticated ? <RoleHomeRedirect /> : <LandingPage />} />
        <Route path="/login" element={isAuthenticated ? <RoleHomeRedirect /> : <Login />} />
        <Route path="/signup" element={isAuthenticated ? <RoleHomeRedirect /> : <Signup />} />

        <Route
          element={
            <ProtectedRoute>
              <EnterpriseAppLayout />
            </ProtectedRoute>
          }
        >
          <Route
            path="/candidate"
            element={
              <ProtectedRoute allowedRoles={["candidate"]}>
                <CandidateIntelligencePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/recruiter"
            element={
              <ProtectedRoute allowedRoles={["recruiter", "admin"]}>
                <RecruiterOperationsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminCommandCenterPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/rbac"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <RbacAccessControlPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute allowedRoles={["recruiter", "admin"]}>
                <AnalyticsIntelligencePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/candidates"
            element={
              <ProtectedRoute allowedRoles={["recruiter", "admin"]}>
                <RecruiterCandidatesPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/interviews"
            element={
              <ProtectedRoute allowedRoles={["recruiter", "admin"]}>
                <RecruiterInterviewsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/audit-logs"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminAuditLogsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/experiments"
            element={
              <ProtectedRoute allowedRoles={["admin"]}>
                <AdminExperimentsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/profile" element={<CandidateProfile />} />
          <Route path="/mock-interview" element={<MockInterview />} />
          <Route path="/interview-history" element={<InterviewHistory />} />
          <Route path="/notifications" element={<CandidateNotifications />} />
        </Route>

        <Route
          path="/interview-session"
          element={
            <ProtectedRoute>
              <InterviewPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/report"
          element={
            <ProtectedRoute>
              <CandidateInterviewReport />
            </ProtectedRoute>
          }
        />

        <Route path="/dashboard" element={<RoleHomeRedirect />} />
        <Route path="/logout" element={<LogoutRoute />} />
        <Route path="*" element={<Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />} />
      </Routes>
    </Suspense>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <HashRouter>
        <AppContent />
      </HashRouter>
    </ErrorBoundary>
  );
}

