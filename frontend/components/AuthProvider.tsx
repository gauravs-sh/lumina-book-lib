"use client";

import { createContext, ReactNode, useCallback, useContext, useMemo, useState } from "react";
import { decodeEmail, getToken, setToken } from "../lib/auth";

interface AuthContextValue {
  token: string | null;
  email: string | null;
  setAuthToken: (value: string | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setTokenState] = useState<string | null>(getToken());

  const setAuthToken = useCallback((value: string | null) => {
    setToken(value);
    setTokenState(value);
  }, []);

  const logout = useCallback(() => setAuthToken(null), [setAuthToken]);
  const email = useMemo(() => decodeEmail(token), [token]);

  const value = useMemo(
    () => ({ token, email, setAuthToken, logout }),
    [token, email, setAuthToken, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
