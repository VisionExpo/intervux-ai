import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePageMeta } from "../hooks/usePageMeta";

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
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-[2rem] border border-slate-200 bg-white p-8 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-500 text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-slate-900">Intervux AI</p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Enterprise Workspace</p>
          </div>
        </div>

        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Sign in</h1>
        <p className="mt-1 text-sm text-slate-500">Access your AI hiring intelligence command center.</p>

        {error ? <p className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-400"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-400"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>
          <button disabled={isLoading} className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60">
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
          <p className="font-semibold text-slate-700">Demo Credentials</p>
          <p>Admin: admin@intervux.ai / admin123</p>
          <p>Recruiter: recruiter@intervux.ai / recruiter123</p>
        </div>

        <p className="mt-5 text-sm text-slate-600">
          No account yet? <Link to="/signup" className="font-semibold text-blue-700">Create candidate account</Link>
        </p>
      </div>
    </div>
  );
}

