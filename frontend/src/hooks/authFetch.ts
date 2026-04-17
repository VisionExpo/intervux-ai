export const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
export const AUTH_UNAUTHORIZED_EVENT = "auth:unauthorized";

// Helper function for authenticated fetch
export async function authFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const isDemo = window.location.hash.includes('demo=true');
  const token = localStorage.getItem("auth_token");
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 && !isDemo) {
      // Token expired or invalid
      localStorage.removeItem("auth_token");
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
      window.location.hash = "#/login";
      throw new Error("Unauthorized");
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}
