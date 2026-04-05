import { useEffect, useState } from "react";
import { useAuth } from "./hooks/useAuth";
import AppShell from "./components/AppShell";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import CandidateDashboard from "./pages/CandidateDashboard";
import CandidateProfile from "./pages/CandidateProfile";
import MockInterview from "./pages/MockInterview";
import InterviewHistory from "./pages/InterviewHistory";
import CandidateNotifications from "./pages/CandidateNotifications";
import InterviewPage from "./pages/InterviewPage";
import CandidateInterviewReport from "./pages/CandidateInterviewReport";
import "./App.css";

function getRoute(): string {
  return window.location.hash.replace("#", "").split("?")[0] || "/dashboard";
}

function App() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [hash, setHash] = useState(getRoute);

  useEffect(() => {
    const handleHashChange = () => setHash(getRoute());
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  // After login, redirect to dashboard if still at root
  useEffect(() => {
    if (isAuthenticated && (!window.location.hash || window.location.hash === "#/")) {
      window.location.hash = "#/dashboard";
    }
  }, [isAuthenticated]);

  if (isLoading) {
    return (
      <div className="login-page">
      <div className="login-container loading-screen">
        <div className="loading-icon">⚡</div>
        <p className="loading-text">Loading Intervux AI...</p>
      </div>
    </div>
    );
  }

  if (!isAuthenticated) {
    if (hash === "/signup") return <Signup />;
    return <Login />;
  }

  const userRole = user?.role;

  if (userRole === "candidate") {
    // Pages that use the full-screen interview layout (no sidebar)
    if (hash === "/interview-session") return <InterviewPage />;
    if (hash === "/report")            return <CandidateInterviewReport />;
    if (hash === "/logout")            return <LogoutRedirect />;

    // All other candidate pages get the sidebar shell
    const page = (() => {
      switch (hash) {
        case "/dashboard":         return <CandidateDashboard />;
        case "/profile":           return <CandidateProfile />;
        case "/mock-interview":    return <MockInterview />;
        case "/interview-history": return <InterviewHistory />;
        case "/notifications":     return <CandidateNotifications />;
        default:                   return <CandidateDashboard />;
      }
    })();

    return <AppShell currentPath={hash}>{page}</AppShell>;
  }

  if (userRole === "admin") {
    return <AdminDashboard />;
  }

  // Recruiter
  return <RecruiterDashboard />;
}

export default App;

function LogoutRedirect() {
  useEffect(() => {
    localStorage.removeItem("auth_token");
    window.location.hash = "#/";
    window.location.reload();
  }, []);
  return (
    <div className="login-page">
      <div className="login-container loading-screen">
        <p className="loading-text">Logging out...</p>
      </div>
    </div>
  );
}
