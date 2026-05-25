"use client";

/**
 * Security tab — password change form (moved verbatim from settings/page.tsx A2).
 * Includes re-auth challenge (current_password field).
 */

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Eye, EyeOff, Lock } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { createClient } from "@/lib/supabase/client";
import { MfaSection } from "@/components/settings/mfa-section";

// ── component ─────────────────────────────────────────────────────────────────

export function SecurityTab() {
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  // ── password state ─────────────────────────────────────────────────────────
  const [currentPw, setCurrentPw]                   = useState("");
  const [pw, setPw]                                 = useState("");
  const [confirmPw, setConfirmPw]                   = useState("");
  const [pwError, setPwError]                       = useState<string | null>(null);
  const [pwSuccess, setPwSuccess]                   = useState(false);
  const [pwSubmitting, setPwSubmitting]             = useState(false);
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword]       = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // ── handler ────────────────────────────────────────────────────────────────

  async function onChangePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwError(null);
    setPwSuccess(false);
    if (!currentPw) { setPwError("Please enter your current password."); return; }
    if (pw.length < 8) { setPwError("Password must be at least 8 characters."); return; }
    if (pw !== confirmPw) { setPwError("Passwords don't match."); return; }
    if (currentPw === pw) { setPwError("New password must differ from current password."); return; }
    setPwSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setPwError("Please sign in again."); return; }
      const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
      const resp = await fetch(`${ENGINE_BASE}/api/account/change-password`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ current_password: currentPw, new_password: pw }),
      });
      const result = await resp.json();
      if (resp.ok) {
        setCurrentPw(""); setPw(""); setConfirmPw(""); setPwSuccess(true);
      } else {
        setPwError(result.error || "Could not change password. Please try again.");
      }
    } catch (err) {
      setPwError(err instanceof Error ? err.message : "Password update failed.");
    } finally {
      setPwSubmitting(false);
    }
  }

  if (!user) return null;

  return (
    <div className="space-y-8">
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <div className="flex items-center gap-2 text-foreground">
          <Lock className="w-5 h-5 text-muted-foreground" />
          <h2 className={`${type.dashboard.heading.l}`}>Change password</h2>
        </div>
        <form onSubmit={onChangePassword} className="space-y-3">
          <label className="block">
            <span className={`${type.label} text-muted-foreground`}>Current password</span>
            <div className="relative mt-1">
              <input
                type={showCurrentPassword ? "text" : "password"}
                value={currentPw} onChange={(e) => setCurrentPw(e.target.value)}
                required autoComplete="current-password"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                type="button"
                onClick={() => setShowCurrentPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label={showCurrentPassword ? "Hide password" : "Show password"}
              >
                {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </label>
          <label className="block">
            <span className={`${type.label} text-muted-foreground`}>New password</span>
            <div className="relative mt-1">
              <input
                type={showNewPassword ? "text" : "password"}
                value={pw} onChange={(e) => setPw(e.target.value)}
                required minLength={8} autoComplete="new-password"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                type="button"
                onClick={() => setShowNewPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label={showNewPassword ? "Hide password" : "Show password"}
              >
                {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </label>
          <label className="block">
            <span className={`${type.label} text-muted-foreground`}>Confirm new password</span>
            <div className="relative mt-1">
              <input
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)}
                required minLength={8} autoComplete="new-password"
                className="w-full rounded-lg border border-border bg-background px-3 py-2 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <button
                type="button"
                onClick={() => setShowConfirmPassword(v => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                aria-label={showConfirmPassword ? "Hide password" : "Show password"}
              >
                {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </label>
          {pwError && <p className={`${type.body.s} text-destructive`} role="alert">{pwError}</p>}
          {pwSuccess && (
            <p className={`${type.body.s} text-primary`} role="status">
              Password changed. Other sessions have been signed out. We emailed you a confirmation.
            </p>
          )}
          <button
            type="submit" disabled={pwSubmitting}
            className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {pwSubmitting ? "Updating…" : "Update password"}
          </button>
        </form>
      </motion.section>

      {/* Phase D.1 (2026-05-24) — TOTP MFA enrollment + disable flow. */}
      <MfaSection />
    </div>
  );
}
