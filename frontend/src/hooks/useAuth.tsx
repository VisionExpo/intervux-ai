/* eslint-disable react-refresh/only-export-components */
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

import { API_BASE_URL, AUTH_UNAUTHORIZED_EVENT } from "./authFetch";

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
  const resetAuthState = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  // Fetch user profile on mount if token exists
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem("auth_token");
      const expiry = localStorage.getItem("auth_token_expires");

      if (storedToken) {
        if (expiry && Date.now() > parseInt(expiry, 10)) {
          localStorage.removeItem("auth_token");
          localStorage.removeItem("auth_token_expires");
          resetAuthState();
          setIsLoading(false);
          return;
        }

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
            localStorage.removeItem("auth_token_expires");
          localStorage.removeItem("auth_token");
            resetAuthState();
          }
        } catch {
          localStorage.removeItem("auth_token_expires");
          localStorage.removeItem("auth_token");
          resetAuthState();
        }
      }
      setIsLoading(false);
    };
    void initAuth();
  }, [resetAuthState]);

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
    const expiresAt = Date.now() + (data.expires_in || 3600) * 1000;
    localStorage.setItem("auth_token", accessToken);
    localStorage.setItem("auth_token_expires", expiresAt.toString());
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
    localStorage.removeItem("auth_token_expires");
    resetAuthState();
  }, [resetAuthState]);

  useEffect(() => {
    const handleUnauthorized = () => {
      resetAuthState();
    };

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized); window._authExpiryInterval = setInterval(() => { const exp = localStorage.getItem("auth_token_expires"); if (exp && Date.now() > parseInt(exp)) logout(); }, 30000);
    return () => {
      window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized); clearInterval(window._authExpiryInterval);
    };
  }, [resetAuthState]);

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


