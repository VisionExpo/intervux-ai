export const API_BASE_URL = import.meta.env.VITE_API_URL;
export const AUTH_UNAUTHORIZED_EVENT = "auth:unauthorized";

// Helper function for authenticated fetch
export async function authFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("auth_token");
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  const expiry = localStorage.getItem("auth_token_expires");

  if (token && expiry && Date.now() > parseInt(expiry, 10)) {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("auth_token_expires");
    window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
    window.location.hash = "#/login";
    throw new Error("Session expired. Please login again.");
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_token_expires");
      window.dispatchEvent(new CustomEvent(AUTH_UNAUTHORIZED_EVENT));
      window.location.hash = "#/login";
      throw new Error("Unauthorized");
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}
