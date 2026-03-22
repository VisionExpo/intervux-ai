import { useEffect, useState } from "react";
import { useAuth } from "./hooks/useAuth";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import CandidateDashboard from "./pages/CandidateDashboard";
import CandidateProfile from "./pages/CandidateProfile";
import MockInterview from "./pages/MockInterview";
import InterviewHistory from "./pages/InterviewHistory";
import CandidateNotifications from "./pages/CandidateNotifications";
import InterviewPage from "./pages/InterviewPage";
import CandidateInterviewReport from "./pages/CandidateInterviewReport";
import "./App.css";

function App() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const currentRoute = () =>
    (window.location.hash.replace("#", "").split("?")[0] || "/profile");
  const [hash, setHash] = useState(currentRoute);

  // Listen for hash changes
  useEffect(() => {
    const handleHashChange = () => {
      const newHash = currentRoute();
      setHash(newHash);
    };

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  if (isLoading) {
    return (
      <div className="login-page">
        <div className="login-container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // For non-authenticated users, show login/signup
  if (!isAuthenticated) {
    // Check if we're on signup route
    if (hash === "/signup") {
      return <Signup />;
    }
    return <Login />;
  }

  // Route based on user role
  const userRole = user?.role;

  if (userRole === "candidate") {
    // Candidate portal routes - use hash-based routing for simplicity
    switch (hash) {
      case "/dashboard":
        return <CandidateDashboard />;
      case "/profile":
        return <CandidateProfile />;
      case "/mock-interview":
        return <MockInterview />;
      case "/interview-session":
        return <InterviewPage />;
      case "/report":
        return <CandidateInterviewReport />;
      case "/interview-history":
        return <InterviewHistory />;
      case "/notifications":
        return <CandidateNotifications />;
      case "/logout":
        // Handle logout
        localStorage.removeItem("auth_token");
        window.location.hash = "#/login";
        window.location.reload();
        return <Login />;
      default:
        return <CandidateProfile />;
    }
  }

  // Default to recruiter dashboard for admin/recruiter roles
  return <RecruiterDashboard />;
}

export default App;
