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
    const hash = window.location.hash;
    const isDemoQuery = hash.includes('demo=true');
    
    const initAuth = async () => {
      // Priority: URL param > localStorage demo flag > standard auth
      let demoRole = null;
      if (isDemoQuery) {
        const hashParts = hash.split('?');
        const params = new URLSearchParams(hashParts[1] || '');
        demoRole = params.get('role');
        if (demoRole) localStorage.setItem('intervux_demo_role', demoRole);
      } else {
        demoRole = localStorage.getItem('intervux_demo_role');
      }

      if (isDemoQuery || demoRole) {
        const activeRole = demoRole || 'admin';
        setUser({ 
          id: 'demo-123', 
          email: `demo-${activeRole}@intervux.ai`, 
          name: `Demo Hero`, 
          role: activeRole as string 
        });
        setIsLoading(false);
        return;
      }

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
            resetAuthState();
          }
        } catch {
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
    resetAuthState();
  }, [resetAuthState]);

  useEffect(() => {
    const handleUnauthorized = () => {
      if (!window.location.hash.includes('demo=true')) {
        resetAuthState();
      }
    };

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => {
      window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
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
        isAuthenticated: !!token && !!user || window.location.hash.includes('demo=true'),
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


