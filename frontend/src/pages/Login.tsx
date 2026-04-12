import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePageMeta } from "../hooks/usePageMeta";
import styles from "./Auth.module.css";

export default function Login() {
  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  usePageMeta("Sign In | Intervux AI", "Sign in to access the Intervux AI enterprise hiring intelligence workspace.");

  useEffect(() => {
    if (!isAuthenticated) return;
    const role = user?.role;
    if (role === "admin") navigate("/admin", { replace: true });
    else if (role === "recruiter") navigate("/recruiter", { replace: true });
    else navigate("/candidate", { replace: true });
  }, [isAuthenticated, navigate, user?.role]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.authRoot}>
      <div className={styles.bgGradient} />
      <div className={styles.bgOrbs} />
      
      <div className={styles.authCard}>
        <div className={styles.brandHeader}>
          <div className={styles.brandIcon}>
            <Sparkles size={18} />
          </div>
          <div>
            <h2 className={styles.brandTitle}>Intervux AI</h2>
            <p className={styles.brandSubtext}>Enterprise Workspace</p>
          </div>
        </div>

        <h1 className={styles.pageTitle}>Sign in</h1>
        <p className={styles.pageSubtitle}>Access your AI hiring intelligence command center.</p>

        {error ? <div className={styles.errorBox}>{error}</div> : null}

        <form onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <label className={styles.inputLabel} htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className={styles.inputField}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div className={styles.inputGroup}>
            <label className={styles.inputLabel} htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className={styles.inputField}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <button disabled={isLoading} className={styles.submitBtn}>
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className={styles.demoBox}>
          <p className={styles.demoBoxTitle}>Demo Credentials</p>
          <p>Admin: admin@intervux.ai / admin123</p>
          <p>Recruiter: recruiter@intervux.ai / recruiter123</p>
        </div>

        <div className={styles.authFooter}>
          No account yet? <Link to="/signup" className={styles.authLink}>Create candidate account</Link>
        </div>
      </div>
    </div>
  );
}
