import { useAuth } from "./hooks/useAuth";
import Login from "./pages/Login";
import RecruiterDashboard from "./pages/RecruiterDashboard";
import "./App.css";

function App() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="login-page">
        <div className="login-container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return <RecruiterDashboard />;
}

export default App;
