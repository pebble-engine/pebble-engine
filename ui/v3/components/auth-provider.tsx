"use client";

/**
 * AuthProvider — wraps the app, exposes the current user + sign-in/out
 * helpers via the useAuth() hook. Cookies are HttpOnly, so we keep the
 * public user object in memory and refetch on mount.
 *
 * Public surface:
 *   const { user, loading, signIn, signUp, signOut, refresh } = useAuth();
 *
 * user === null means signed out (or check still loading when `loading` is true).
 */

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { fetchMe, login as apiLogin, logout as apiLogout, signup as apiSignup, type AuthUser } from "@/lib/auth";

type AuthContextValue = {
  user:    AuthUser | null;
  loading: boolean;
  signIn:  (email: string, password: string) => Promise<AuthUser>;
  signUp:  (email: string, password: string) => Promise<AuthUser>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const me = await fetchMe();
    setUser(me);
    setLoading(false);
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const signIn = useCallback(async (email: string, password: string) => {
    const { user } = await apiLogin(email, password);
    setUser(user);
    return user;
  }, []);

  const signUp = useCallback(async (email: string, password: string) => {
    const { user } = await apiSignup(email, password);
    setUser(user);
    return user;
  }, []);

  const signOut = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
