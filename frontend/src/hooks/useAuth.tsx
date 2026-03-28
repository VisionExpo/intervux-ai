import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem("auth_token");
  });
  const [isLoading, setIsLoading] = useState(true);

  // Fetch user profile on mount if token exists
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("auth_token");
      if (storedToken) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          });
          if (response.ok) {
            const userData = await response.json();
            setUser({
              id: userData.id,
              email: userData.email,
              name: userData.name,
              role: userData.role,
            });
            setToken(storedToken);
          } else {
            // Token invalid, clear it
            localStorage.removeItem("auth_token");
          }
        } catch {
          localStorage.removeItem("auth_token");
        }
      }
      setIsLoading(false);
    };
    void initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append("username", email);
    formData.append("password", password);

    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(error.detail || "Login failed");
    }

    const data: LoginResponse = await response.json();
    const accessToken = data.access_token;

    // Store token
    localStorage.setItem("auth_token", accessToken);
    setToken(accessToken);

    // Fetch user profile
    const userResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    if (userResponse.ok) {
      const userData = await userResponse.json();
      setUser({
        id: userData.id,
        email: userData.email,
        name: userData.name,
        role: userData.role,
      });
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("auth_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        logout,
        isAuthenticated: !!token && !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

// Helper function for authenticated fetch
export async function authFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
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
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem("auth_token");
      window.location.hash = "#/login";
      throw new Error("Unauthorized");
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}

