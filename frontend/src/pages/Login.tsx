import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePageMeta } from "../hooks/usePageMeta";
import { Input } from "../components/ui/Input/Input";
import { Button } from "../components/ui/Button/Button";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
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
      
      <div className={styles.authCardWrapper}>
        <GlassCard padding="lg">
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
            <div className={styles.formGrid}>
              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
              <Input
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            </div>
            <Button disabled={isLoading} fullWidth type="submit">
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </form>

          <div className={styles.authFooter}>
            No account yet? <Link to="/signup" className={styles.authLink}>Create candidate account</Link>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
