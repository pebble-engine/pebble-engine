"use client";

/**
 * SessionsSection — active-sessions table inside the Security tab.
 * Phase D.2 (2026-05-24).
 *
 * Backed by:
 *   GET    /api/account/sessions               — list
 *   DELETE /api/account/sessions/<id>          — revoke one
 *   (Global sign-out lives in <GlobalSignoutSection /> alongside.)
 *
 * Each row shows:
 *   - Device summary (parsed from user agent)
 *   - IP address
 *   - Last activity (refreshed_at, falling back to updated_at)
 *   - "This device" badge when UA + IP match the current request
 *   - Revoke button (disabled for this-device — use global sign-out instead)
 */

import { useEffect, useMemo, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Loader2, Monitor, RefreshCw, Smartphone, Trash2 } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { createClient } from "@/lib/supabase/client";

type SessionRow = {
  id: string;
  created_at: string | null;
  updated_at: string | null;
  refreshed_at: string | null;
  not_after: string | null;
  user_agent: string;
  user_agent_summary: string;
  ip: string;
  aal: string | null;
  is_current: boolean;
};

type FetchState =
  | { phase: "loading" }
  | { phase: "loaded"; sessions: SessionRow[] }
  | { phase: "error"; message: string };

function formatRelative(iso: string | null): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return iso;
  const diffMs = Date.now() - then;
  const minutes = Math.floor(diffMs / 60_000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hr ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days} day${days === 1 ? "" : "s"} ago`;
  return new Date(iso).toLocaleDateString();
}

function isMobileSummary(summary: string): boolean {
  const s = summary.toLowerCase();
  return s.includes("iphone") || s.includes("android") || s.includes("ipad");
}

export function SessionsSection() {
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  const [state, setState] = useState<FetchState>({ phase: "loading" });
  const [revokingId, setRevokingId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState({ phase: "loading" });
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) {
        setState({ phase: "error", message: "Sign in to view active sessions." });
        return;
      }
      const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
      const resp = await fetch(`${ENGINE_BASE}/api/account/sessions`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await resp.json().catch(() => ({}));
      if (!resp.ok) {
        setState({
          phase: "error",
          message: body?.error || "Couldn't load active sessions. Please try again.",
        });
        return;
      }
      setState({ phase: "loaded", sessions: body.sessions || [] });
    } catch (e) {
      setState({
        phase: "error",
        message: e instanceof Error ? e.message : "Couldn't load active sessions.",
      });
    }
  }, [supabase]);

  useEffect(() => {
    if (user) load();
  }, [user, load]);

  async function revokeOne(id: string) {
    if (!confirm("Sign out this session? The device will need to sign in again.")) return;
    setRevokingId(id);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) return;
      const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
      const resp = await fetch(`${ENGINE_BASE}/api/account/sessions/${encodeURIComponent(id)}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (resp.ok) {
        // Optimistic remove
        setState((prev) =>
          prev.phase === "loaded"
            ? { phase: "loaded", sessions: prev.sessions.filter((s) => s.id !== id) }
            : prev,
        );
      } else {
        const body = await resp.json().catch(() => ({}));
        alert(body?.error || "Couldn't revoke that session.");
      }
    } finally {
      setRevokingId(null);
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="rounded-2xl border border-border bg-card p-6 space-y-4"
    >
      <div className="flex items-center justify-between gap-2 text-foreground">
        <div className="flex items-center gap-2">
          <Monitor className="w-5 h-5 text-muted-foreground" />
          <h2 className={`${type.dashboard.heading.l}`}>Where you're signed in</h2>
        </div>
        <button
          type="button"
          onClick={load}
          disabled={state.phase === "loading"}
          aria-label="Refresh sessions"
          className="inline-flex items-center gap-1 rounded-full border border-border px-3 py-1 text-xs font-medium text-muted-foreground hover:bg-muted/50 disabled:opacity-50"
        >
          <RefreshCw
            className={`w-3 h-3 ${state.phase === "loading" ? "animate-spin" : ""}`}
          />
          Refresh
        </button>
      </div>
      <p className={`${type.body.s} text-muted-foreground`}>
        Each row is an active sign-in on a device. If you see something you don't
        recognize, revoke it — and consider changing your password.
      </p>

      {state.phase === "loading" && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading your sessions…
        </div>
      )}

      {state.phase === "error" && (
        <p className={`${type.body.s} text-destructive`} role="alert">
          {state.message}
        </p>
      )}

      {state.phase === "loaded" && state.sessions.length === 0 && (
        <p className={`${type.body.s} text-muted-foreground`}>
          No active sessions found. (This is unusual — try refreshing.)
        </p>
      )}

      {state.phase === "loaded" && state.sessions.length > 0 && (
        <ul className="divide-y divide-border rounded-lg border border-border">
          {state.sessions.map((s) => {
            const Icon = isMobileSummary(s.user_agent_summary) ? Smartphone : Monitor;
            const lastSeen = s.refreshed_at || s.updated_at || s.created_at;
            return (
              <li key={s.id} className="flex items-center justify-between gap-3 p-3">
                <div className="flex items-start gap-3 min-w-0 flex-1">
                  <Icon className="w-5 h-5 text-muted-foreground shrink-0 mt-0.5" />
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-baseline gap-2">
                      <span className={`${type.body.s} font-medium text-foreground truncate`}>
                        {s.user_agent_summary || "Unknown device"}
                      </span>
                      {s.is_current && (
                        <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-primary">
                          This device
                        </span>
                      )}
                    </div>
                    <div className={`${type.caption} mt-0.5`}>
                      {s.ip || "Unknown IP"} · last active {formatRelative(lastSeen)}
                    </div>
                  </div>
                </div>
                {/* Disable revoke on this-device: send users to the global sign-out
                    flow instead — it has the email-notify path. */}
                <button
                  type="button"
                  onClick={() => revokeOne(s.id)}
                  disabled={s.is_current || revokingId === s.id}
                  aria-label="Revoke this session"
                  title={
                    s.is_current
                      ? "Use Sign out everywhere to end this session"
                      : "Sign out this session"
                  }
                  className="inline-flex items-center gap-1 rounded-full border border-destructive/40 px-3 py-1 text-xs font-medium text-destructive hover:bg-destructive/10 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  {revokingId === s.id ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Trash2 className="w-3 h-3" />
                  )}
                  Revoke
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </motion.section>
  );
}
