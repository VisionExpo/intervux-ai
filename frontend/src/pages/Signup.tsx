import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { useAuth } from "../hooks/useAuth";
import { usePageMeta } from "../hooks/usePageMeta";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export default function Signup() {
  const { login } = useAuth();
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
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md rounded-[2rem] border border-slate-200 bg-white p-8 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-600 to-indigo-500 text-white">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <p className="font-semibold text-slate-900">Intervux AI</p>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Candidate Onboarding</p>
          </div>
        </div>

        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Create account</h1>
        <p className="mt-1 text-sm text-slate-500">Start your AI-guided interview intelligence journey.</p>

        {error ? <p className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p> : null}

        <form className="mt-5 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="name">Full name</label>
            <input id="name" type="text" className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-400" value={name} onChange={(event) => setName(event.target.value)} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="email">Email</label>
            <input id="email" type="email" className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-400" value={email} onChange={(event) => setEmail(event.target.value)} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="password">Password</label>
            <input id="password" type="password" className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-400" value={password} onChange={(event) => setPassword(event.target.value)} required />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700" htmlFor="confirmPassword">Confirm password</label>
            <input id="confirmPassword" type="password" className="w-full rounded-xl border border-slate-200 px-3 py-2.5 text-sm outline-none transition focus:border-blue-400" value={confirmPassword} onChange={(event) => setConfirmPassword(event.target.value)} required />
          </div>
          <button disabled={isLoading} className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60">
            {isLoading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-5 text-sm text-slate-600">
          Already have an account? <Link to="/login" className="font-semibold text-blue-700">Sign in</Link>
        </p>
      </div>
    </div>
  );
}

