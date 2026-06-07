"use client";

/**
 * Profile tab — display name, timezone, avatar, email display,
 * and email-change form (moved verbatim from settings/page.tsx A4).
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Mail, User } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { createClient } from "@/lib/supabase/client";
import { BusinessKnowledgeCard } from "@/components/workspace/business-knowledge-card";
import { getAccountKnowledge, saveAccountKnowledge } from "@/lib/api";

// ── types ─────────────────────────────────────────────────────────────────────

interface ProfileState {
  first_name: string | null;
  display_name: string | null;
  timezone: string;
  deletion_scheduled_for: string | null;
}

// ── helpers ───────────────────────────────────────────────────────────────────

/** DiceBear avatar URL — letter-initial avatar from any email seed. */
function avatarUrl(email: string): string {
  return `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(email)}&backgroundColor=f59e0b&textColor=ffffff&fontSize=40`;
}

// Common IANA timezones for the dropdown (covers ~95% of users).
const COMMON_TIMEZONES = [
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "America/Phoenix",
  "America/Anchorage",
  "Pacific/Honolulu",
  "America/Toronto",
  "America/Vancouver",
  "America/Sao_Paulo",
  "America/Argentina/Buenos_Aires",
  "America/Mexico_City",
  "Europe/London",
  "Europe/Paris",
  "Europe/Berlin",
  "Europe/Madrid",
  "Europe/Rome",
  "Europe/Amsterdam",
  "Europe/Warsaw",
  "Europe/Kiev",
  "Europe/Moscow",
  "Asia/Dubai",
  "Asia/Karachi",
  "Asia/Kolkata",
  "Asia/Dhaka",
  "Asia/Bangkok",
  "Asia/Singapore",
  "Asia/Shanghai",
  "Asia/Tokyo",
  "Asia/Seoul",
  "Australia/Sydney",
  "Australia/Melbourne",
  "Pacific/Auckland",
];

// ── component ─────────────────────────────────────────────────────────────────

export function ProfileTab() {
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  // ── profile state ──────────────────────────────────────────────────────────
  const [profile, setProfile]                   = useState<ProfileState | null>(null);
  const [profileLoading, setProfileLoading]     = useState(true);
  const [firstName, setFirstName]               = useState("");
  const [displayName, setDisplayName]           = useState("");
  const [timezone, setTimezone]                 = useState("UTC");
  const [profileSaving, setProfileSaving]       = useState(false);
  const [profileSuccess, setProfileSuccess]     = useState(false);
  const [profileError, setProfileError]         = useState<string | null>(null);

  // ── email-change state ─────────────────────────────────────────────────────
  const [showEmailChange, setShowEmailChange]           = useState(false);
  const [emailChangePw, setEmailChangePw]               = useState("");
  const [newEmail, setNewEmail]                         = useState("");
  const [emailChangeError, setEmailChangeError]         = useState<string | null>(null);
  const [emailChangeSuccess, setEmailChangeSuccess]     = useState<string | null>(null);
  const [emailChangeSubmitting, setEmailChangeSubmitting] = useState(false);

  // ── load profile ───────────────────────────────────────────────────────────
  const loadProfile = useCallback(async () => {
    if (!user) return;
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) return;
      const res = await fetch("/api/account/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const p: ProfileState = await res.json();
      setProfile(p);
      setFirstName(p.first_name ?? "");
      setDisplayName(p.display_name ?? "");
      setTimezone(p.timezone ?? "UTC");
    } catch {
      // non-fatal
    } finally {
      setProfileLoading(false);
    }
  }, [user, supabase]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  // ── handlers ───────────────────────────────────────────────────────────────

  async function onSaveProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileError(null);
    setProfileSuccess(false);
    setProfileSaving(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setProfileError("Not authenticated."); return; }
      const res = await fetch("/api/account/profile", {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ first_name: firstName.trim() || null, display_name: displayName.trim() || null, timezone }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        setProfileError((err as { error?: string }).error || "Profile update failed.");
        return;
      }
      setProfileSuccess(true);
    } catch (err) {
      setProfileError(err instanceof Error ? err.message : "Profile update failed.");
    } finally {
      setProfileSaving(false);
    }
  }

  async function onChangeEmail(e: React.FormEvent) {
    e.preventDefault();
    setEmailChangeError(null);
    setEmailChangeSuccess(null);
    if (!emailChangePw) { setEmailChangeError("Please enter your current password."); return; }
    if (!newEmail || !newEmail.includes("@")) {
      setEmailChangeError("Please enter a valid email address."); return;
    }
    if (newEmail.toLowerCase() === (user?.email ?? "").toLowerCase()) {
      setEmailChangeError("New email must differ from your current email."); return;
    }
    setEmailChangeSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setEmailChangeError("Please sign in again."); return; }
      const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
      const resp = await fetch(`${ENGINE_BASE}/api/account/change-email-request`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ current_password: emailChangePw, new_email: newEmail }),
      });
      const result = await resp.json();
      if (resp.ok) {
        setEmailChangePw("");
        setNewEmail("");
        setShowEmailChange(false);
        setEmailChangeSuccess(result.message || "Confirmation email sent. Check your new inbox.");
      } else {
        setEmailChangeError(result.error || "Could not send confirmation email. Please try again.");
      }
    } catch (err) {
      setEmailChangeError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setEmailChangeSubmitting(false);
    }
  }

  if (!user) return null;

  return (
    <div className="space-y-8">

      {/* ── Avatar + email display ─────────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-5"
      >
        <div className="flex items-center gap-2 text-foreground">
          <User className="w-5 h-5 text-muted-foreground" />
          <h2 className={`${type.dashboard.heading.l}`}>Profile</h2>
        </div>

        {/* Avatar + email */}
        <div className="flex items-center gap-4">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={avatarUrl(user.email ?? "")}
            alt="avatar"
            width={56} height={56}
            className="rounded-full border-2 border-border bg-muted"
          />
          <div>
            <p className="font-medium text-foreground">{user.email}</p>
            <p className={type.caption}>Avatar generated from your email</p>
          </div>
        </div>

        {profileLoading ? (
          <div className="h-24 bg-muted/40 rounded-lg animate-pulse" />
        ) : (
          <form onSubmit={onSaveProfile} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <label className="block">
                <span className={`${type.label} text-muted-foreground`}>First name</span>
                <input
                  type="text"
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="Jane"
                  maxLength={100}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
              <label className="block">
                <span className={`${type.label} text-muted-foreground`}>Display name</span>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  placeholder="Jane Smith"
                  maxLength={100}
                  className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </label>
            </div>
            <label className="block">
              <span className={`${type.label} text-muted-foreground`}>Time zone</span>
              <select
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {COMMON_TIMEZONES.map((tz) => (
                  <option key={tz} value={tz}>{tz.replace(/_/g, " ")}</option>
                ))}
              </select>
            </label>
            {profileError && (
              <p className={`${type.body.s} text-destructive`} role="alert">{profileError}</p>
            )}
            {profileSuccess && (
              <p className={`${type.body.s} text-primary`} role="status">Profile saved.</p>
            )}
            <button
              type="submit" disabled={profileSaving}
              className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {profileSaving ? "Saving…" : "Save profile"}
            </button>
          </form>
        )}
      </motion.section>

      {/* ── Email section ──────────────────────────────────────────────────── */}
      <motion.section
        initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.04 }}
        className="rounded-2xl border border-border bg-card p-6 space-y-4"
      >
        <div className="flex items-center gap-2 text-foreground">
          <Mail className="w-5 h-5 text-muted-foreground" />
          <h2 className={`${type.dashboard.heading.l}`}>Email address</h2>
        </div>

        <div className="space-y-1">
          <p className={type.caption}>Signed in as</p>
          <p className="text-foreground font-medium">{user.email}</p>
        </div>

        {/* Email-change success banner */}
        {emailChangeSuccess && (
          <div className="rounded-xl border border-primary/30 bg-primary/5 p-3">
            <p className={`${type.body.s} text-primary`}>{emailChangeSuccess}</p>
          </div>
        )}

        {/* Change email toggle */}
        <div>
          <button
            type="button"
            onClick={() => { setShowEmailChange(v => !v); setEmailChangeError(null); setEmailChangeSuccess(null); }}
            className={`flex items-center gap-1.5 ${type.body.s} text-muted-foreground hover:text-foreground`}
          >
            <Mail className="w-3.5 h-3.5" />
            Change email address
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showEmailChange ? "rotate-180" : ""}`} />
          </button>
          <AnimatePresence>
            {showEmailChange && (
              <motion.div
                key="email-change-zone"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <form onSubmit={onChangeEmail} className="mt-4 p-4 rounded-xl border border-border bg-background/60 space-y-3">
                  <p className={`${type.body.s} text-muted-foreground`}>
                    We&apos;ll send a confirmation link to your new address. Click it within 24 hours to complete the change.
                  </p>
                  <label className="block">
                    <span className={`${type.label} text-muted-foreground`}>Current password</span>
                    <input
                      type="password"
                      value={emailChangePw}
                      onChange={(e) => setEmailChangePw(e.target.value)}
                      required
                      autoComplete="current-password"
                      className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </label>
                  <label className="block">
                    <span className={`${type.label} text-muted-foreground`}>New email address</span>
                    <input
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      required
                      autoComplete="email"
                      placeholder="new@example.com"
                      className="mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </label>
                  {emailChangeError && (
                    <p className={`${type.body.s} text-destructive`} role="alert">{emailChangeError}</p>
                  )}
                  <button
                    type="submit"
                    disabled={emailChangeSubmitting}
                    className="inline-flex items-center rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {emailChangeSubmitting ? "Sending…" : "Send confirmation link"}
                  </button>
                </form>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.section>

      <BusinessKnowledgeCard
        title="Tell Pebble about your business"
        subtitle="Applies to every site you build. Pebble remembers it so you never repeat yourself."
        load={async () => (await getAccountKnowledge()).knowledge}
        save={async (t) => { await saveAccountKnowledge(t); }}
      />
    </div>
  );
}
