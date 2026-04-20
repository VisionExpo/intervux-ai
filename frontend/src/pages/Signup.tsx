import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePageMeta } from "../hooks/usePageMeta";
import { Input } from "../components/ui/Input/Input";
import { Button } from "../components/ui/Button/Button";
import { GlassCard } from "../components/ui/GlassCard/GlassCard";
import styles from "./Auth.module.css";

const API_BASE_URL = import.meta.env.VITE_API_URL;

export default function Signup() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  usePageMeta("Create Account | Intervux AI", "Create your Intervux AI candidate account and access your intelligence dashboard.");

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/candidate/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name, email, password }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({ detail: "Signup failed" }));
        throw new Error(data.detail || "Signup failed");
      }

      await login(email, password);
      navigate("/candidate", { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
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
              <p className={styles.brandSubtext}>Candidate Onboarding</p>
            </div>
          </div>

          <h1 className={styles.pageTitle}>Create account</h1>
          <p className={styles.pageSubtitle}>Start your AI-guided interview intelligence journey.</p>

          {error ? <div className={styles.errorBox}>{error}</div> : null}

          <form onSubmit={handleSubmit}>
            <div className={styles.formGrid}>
              <Input
                label="Full name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
              />
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
              <Input
                label="Confirm password"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            </div>
            <Button disabled={isLoading} fullWidth type="submit">
              {isLoading ? "Creating account..." : "Create account"}
            </Button>
          </form>

          <div className={styles.authFooter}>
            Already have an account? <Link to="/login" className={styles.authLink}>Sign in</Link>
          </div>
        </GlassCard>
      </div>
    </div>
  );
}
