"use client";

/**
 * AuthProvider — wraps the app and exposes the current user + sign-in
 * helpers via the useAuth() hook. Backed by Supabase Auth as of the
 * 2026-05-16 Phase A migration; the public surface is preserved so the
 * existing /login, /signup, auth-menu, admin pages keep working.
 *
 *   const { user, loading, signIn, signUp, signOut, refresh,
 *           signInWithGoogle, signInWithGithub } = useAuth();
 *
 * user === null means signed out (or check still loading when `loading`
 * is true). All sign-in methods are reflected back into `user` via
 * Supabase's onAuthStateChange listener, so OAuth flows that complete
 * via /auth/callback also surface here without a manual refresh.
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { User } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";

export type AuthUser = {
  id:         string;
  email:      string;
  created_at: string;
};

type AuthContextValue = {
  user:    AuthUser | null;
  loading: boolean;
  signIn:           (email: string, password: string) => Promise<AuthUser>;
  signUp:           (email: string, password: string, firstName?: string) => Promise<AuthUser>;
  signInWithGoogle: () => Promise<void>;
  signInWithGithub: () => Promise<void>;
  signOut:          () => Promise<void>;
  refresh:          () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function toAppUser(u: User): AuthUser {
  return {
    id:         u.id,
    email:      u.email ?? "",
    created_at: u.created_at ?? new Date().toISOString(),
  };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // One client per provider lifetime — re-creating it would tear down
  // the auth-state subscription mid-session.
  const supabase = useMemo(() => createClient(), []);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    const {
      data: { user: u },
    } = await supabase.auth.getUser();
    setUser(u ? toAppUser(u) : null);
    setLoading(false);
  }, [supabase]);

  useEffect(() => {
    refresh();
    // onAuthStateChange fires on sign-in, sign-out, token refresh, and
    // — crucially — when the OAuth callback exchanges its code for a
    // session. Without this listener, OAuth users would land back on
    // /workspace but the in-memory `user` would still be null until
    // they manually reloaded.
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ? toAppUser(session.user) : null);
      setLoading(false);
    });
    return () => subscription.unsubscribe();
  }, [refresh, supabase]);

  const signIn = useCallback(
    async (email: string, password: string) => {
      const { data, error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) throw new Error(error.message);
      if (!data.user) throw new Error("Sign-in returned no user");
      const u = toAppUser(data.user);
      setUser(u);
      return u;
    },
    [supabase],
  );

  const signUp = useCallback(
    async (email: string, password: string, firstName?: string) => {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          // Stored in auth.users.raw_user_meta_data — the 001_profiles.sql
          // trigger reads it to populate profiles.first_name.
          data: firstName ? { first_name: firstName } : undefined,
          emailRedirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent("/workspace")}`,
        },
      });
      if (error) throw new Error(error.message);
      if (!data.user) throw new Error("Sign-up returned no user");
      const u = toAppUser(data.user);
      setUser(u);
      return u;
    },
    [supabase],
  );

  const signInWithOAuth = useCallback(
    async (provider: "google" | "github") => {
      const redirectTo = `${window.location.origin}/auth/callback?next=${encodeURIComponent("/workspace")}`;
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: { redirectTo },
      });
      if (error) throw new Error(error.message);
      // Browser is now navigating away to the provider. No state to set.
    },
    [supabase],
  );

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setUser(null);
  }, [supabase]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signIn,
        signUp,
        signInWithGoogle: () => signInWithOAuth("google"),
        signInWithGithub: () => signInWithOAuth("github"),
        signOut,
        refresh,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
