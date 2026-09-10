import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { authApi } from "../api/authApi";
import { ApiError } from "../api/client";
import type { User } from "../api/types";

type AuthState = {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (body: Record<string, unknown>) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | undefined>(undefined);

const ACCESS = "kc_access";
const REFRESH = "kc_refresh";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(ACCESS));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const current = localStorage.getItem(ACCESS);
    if (!current) {
      setLoading(false);
      return;
    }
    authApi
      .me(current)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(ACCESS);
        localStorage.removeItem(REFRESH);
        setToken(null);
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function applyTokens(access: string, refresh: string) {
    localStorage.setItem(ACCESS, access);
    localStorage.setItem(REFRESH, refresh);
    setToken(access);
    const me = await authApi.me(access);
    setUser(me);
  }

  const value = useMemo<AuthState>(
    () => ({
      user,
      token,
      loading,
      error,
      login: async (email, password) => {
        setError(null);
        try {
          const pair = await authApi.login(email, password);
          await applyTokens(pair.access_token, pair.refresh_token);
        } catch (err) {
          const message = err instanceof ApiError ? err.message : "Could not sign in";
          setError(message);
          throw err;
        }
      },
      register: async (body) => {
        setError(null);
        try {
          const pair = await authApi.register(body);
          await applyTokens(pair.access_token, pair.refresh_token);
        } catch (err) {
          const message = err instanceof ApiError ? err.message : "Could not create account";
          setError(message);
          throw err;
        }
      },
      logout: () => {
        localStorage.removeItem(ACCESS);
        localStorage.removeItem(REFRESH);
        setToken(null);
        setUser(null);
      },
    }),
    [user, token, loading, error],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
