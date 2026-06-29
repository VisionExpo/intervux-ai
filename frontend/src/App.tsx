import { Suspense, lazy, useEffect, type ReactNode } from "react";
import { HashRouter, Navigate, Route, Routes, useNavigate } from "react-router-dom";

import { useAuth } from "./hooks/useAuth";
import { EnterpriseAppLayout } from "./layouts/EnterpriseAppLayout";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { LoadingScreen } from "./components/ui/LoadingScreen/LoadingScreen";
import { InterviewSessionProvider } from "./providers/InterviewSessionProvider";
import { DashboardPreview } from "./pages/DashboardPreview";
import { ComponentPreview } from "./pages/ComponentPreview";

const LandingPage = lazy(() => import("./pages/LandingPage"));
const Login = lazy(() => import("./pages/Login"));
const Signup = lazy(() => import("./pages/Signup"));
const InviteLandingPage = lazy(() => import("./pages/InviteLandingPage"));

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
const Interviews = lazy(() => import("./pages/Interviews"));
const CandidateNotifications = lazy(() => import("./pages/CandidateNotifications"));
const InterviewPage = lazy(() => import("./pages/InterviewPage"));
const CandidateInterviewReport = lazy(() => import("./pages/CandidateInterviewReport"));


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
        <Route path="/invite/:token" element={<InviteLandingPage />} />

        <Route
          element={
            <ProtectedRoute>
              <EnterpriseAppLayout />
            </ProtectedRoute>
          }
        >
          {/* Candidate Routes */}
          <Route path="/candidate" element={<CandidateIntelligencePage />} />
            <Route path="/profile" element={<ProtectedRoute allowedRoles={["candidate"]}><CandidateProfile /></ProtectedRoute>} />
            <Route path="/interviews" element={<ProtectedRoute allowedRoles={["candidate"]}><Interviews /></ProtectedRoute>} />
            <Route path="/mock-interview" element={<Navigate to="/interviews" replace />} />
            <Route path="/interview-history" element={<Navigate to="/interviews" replace />} />
            <Route path="/notifications" element={<ProtectedRoute allowedRoles={["candidate"]}><CandidateNotifications /></ProtectedRoute>} />
          
          {/* Recruiter Routes */}
          <Route path="/recruiter" element={<RecruiterOperationsPage />} />
          <Route path="/candidates" element={<RecruiterCandidatesPage />} />
          <Route path="/interviews" element={<RecruiterInterviewsPage />} />
          <Route path="/analytics" element={<AnalyticsIntelligencePage />} />
          
          {/* Admin Routes */}
          <Route path="/admin" element={<AdminCommandCenterPage />} />
          <Route path="/rbac" element={<RbacAccessControlPage />} />
          <Route path="/audit-logs" element={<AdminAuditLogsPage />} />
          <Route path="/experiments" element={<AdminExperimentsPage />} />
          
          {/* New OS Shell Previews */}
          <Route path="/dashboard-preview" element={<DashboardPreview />} />
          <Route path="/components" element={<ComponentPreview />} />
        </Route>

        <Route
          path="/interview-session"
          element={
            <ProtectedRoute>
              <InterviewSessionProvider>
                <InterviewPage />
              </InterviewSessionProvider>
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

