"use client";

/**
 * GlobalSignoutSection — "Sign out everywhere" CTA inside the Security tab.
 * Phase D.3 (2026-05-24).
 *
 * Flow:
 *   1. Click "Sign out of every device"
 *   2. Inline confirm prompt (no native alert; matches the password-change
 *      form's UX where in-card confirms beat browser dialogs)
 *   3. POST /api/account/global-signout — engine calls Supabase
 *      /auth/v1/logout?scope=global which revokes EVERY refresh token
 *      for the user, including the current one. Engine writes audit_log
 *      + sends defensive-notify email.
 *   4. Clear local Supabase session (the JWT we just sent is now revoked
 *      anyway, but clearing the local storage stops the next render from
 *      thinking we're signed in)
 *   5. Redirect to /login
 *
 * The component is intentionally small + standalone so Phase D.2 can
 * absorb it into the sessions section without a big refactor.
 */

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { LogOut, Loader2, ShieldAlert } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { ENGINE_BASE } from "@/lib/engine-base";
import { createClient } from "@/lib/supabase/client";

type Phase = "idle" | "confirming" | "submitting" | "done" | "error";

export function GlobalSignoutSection() {
  const router = useRouter();
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string>("");

  async function performSignout() {
    if (!user) return;
    setPhase("submitting");
    setError("");
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) {
        // Already signed out somehow — bounce to /login.
        router.replace("/login");
        return;
      }
      const resp = await fetch(`${ENGINE_BASE}/api/account/global-signout`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        setError(body?.error || "Couldn't sign out other sessions. Please try again.");
        setPhase("error");
        return;
      }
      // Supabase already revoked the JWT server-side; clear the local
      // session so the next render doesn't flash a signed-in state.
      try {
        await supabase.auth.signOut({ scope: "local" });
      } catch {
        // ignore — server-side revocation is the source of truth
      }
      setPhase("done");
      // Hard redirect — clears any React Query / context caches that
      // assume a signed-in user.
      router.replace("/login?signed_out=global");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-out failed.");
      setPhase("error");
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="rounded-2xl border border-border bg-card p-6 space-y-4"
    >
      <div className="flex items-center gap-2 text-foreground">
        <LogOut className="w-5 h-5 text-muted-foreground" />
        <h2 className={`${type.dashboard.heading.l}`}>Active sessions</h2>
      </div>
      <p className={`${type.body.s} text-muted-foreground`}>
        If you've signed in on a public computer, lost a device, or just want a clean
        slate, signing out everywhere revokes every session on your account — including
        this one.
      </p>

      {phase === "idle" && (
        <button
          type="button"
          onClick={() => setPhase("confirming")}
          className="inline-flex items-center gap-2 rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/50"
        >
          <LogOut className="w-4 h-4" /> Sign out of every device
        </button>
      )}

      {phase === "confirming" && (
        <div className="space-y-3 rounded-lg border border-destructive/30 bg-destructive/5 p-4">
          <div className="flex items-start gap-2">
            <ShieldAlert className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className={`${type.body.s} font-medium text-foreground`}>
                Sign out of every session on your account?
              </p>
              <p className={`${type.body.s} text-muted-foreground mt-1`}>
                Including this one. You'll need to sign back in to keep working. We'll
                also email you to confirm.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={performSignout}
              className="inline-flex items-center gap-2 rounded-full bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground hover:bg-destructive/90"
            >
              <LogOut className="w-4 h-4" /> Yes, sign out everywhere
            </button>
            <button
              type="button"
              onClick={() => {
                setPhase("idle");
                setError("");
              }}
              className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {phase === "submitting" && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          Signing out every session…
        </div>
      )}

      {phase === "error" && (
        <div className="space-y-3">
          {error && (
            <p className={`${type.body.s} text-destructive`} role="alert">
              {error}
            </p>
          )}
          <button
            type="button"
            onClick={() => setPhase("idle")}
            className="rounded-full border border-border px-4 py-2 text-sm font-medium text-foreground hover:bg-muted/50"
          >
            Try again
          </button>
        </div>
      )}
    </motion.section>
  );
}
