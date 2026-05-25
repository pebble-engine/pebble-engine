"use client";

import { useEffect, useState } from "react";
import { createBrowserClient } from "@supabase/ssr";

const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");

type AuditEvent = {
  id: string;
  event_type: string;
  ip: string | null;
  user_agent: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

// Map raw event_type strings to human-readable labels. Keep
// in sync with the strings written by pebble.audit_log callers.
const EVENT_LABELS: Record<string, string> = {
  password_change:                "Password changed",
  password_change_failed:         "Failed password change attempt",
  email_change_requested:         "Email change requested",
  email_change_confirmed:         "Email address changed",
  email_change_request_failed:    "Email change attempt failed",
  account_delete_requested:       "Account deletion scheduled",
  account_delete_executed:        "Account deleted",
  stripe_subscription_canceled:   "Subscription canceled",
  stripe_subscription_cancel_failed: "Subscription cancel attempt failed",
  plan_changed:                   "Plan changed",
  payment_method_changed:         "Payment method updated",
  mfa_enabled:                    "Two-factor auth enabled",
  mfa_disabled:                   "Two-factor auth disabled",
  signed_in_new_device:           "Signed in from a new device",
  global_signout:                 "Signed out of all devices",
  data_export_requested:          "Data export requested",
  data_export_delivered:          "Data export ready",
};

function formatEvent(t: string): string {
  return EVENT_LABELS[t] || t.replace(/_/g, " ");
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      year: "numeric", month: "short", day: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function ActivityTab() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const supabase = createBrowserClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    );
    supabase.auth.getSession().then(async ({ data }) => {
      const token = data.session?.access_token;
      if (!token) { setStatus("error"); setError("Please sign in again."); return; }
      try {
        const resp = await fetch(`${ENGINE_BASE}/api/account/activity?limit=50`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const body = await resp.json();
        if (resp.ok) {
          setEvents(body.events || []);
          setStatus("ok");
        } else {
          setError(body.error || "Could not load activity.");
          setStatus("error");
        }
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Network error");
        setStatus("error");
      }
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="mb-1 text-lg font-medium">Account activity</h2>
        <p className="text-sm text-muted-foreground">
          A log of security-sensitive actions on your account. If you see something here
          that wasn&apos;t you, change your password immediately and contact support.
        </p>
      </div>

      {status === "loading" && (
        <div className="rounded-lg border p-6 text-center text-sm text-muted-foreground">
          Loading activity&hellip;
        </div>
      )}

      {status === "error" && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4 text-sm text-destructive">
          {error}
        </div>
      )}

      {status === "ok" && events.length === 0 && (
        <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
          No activity yet. This log fills up as you take security-sensitive actions.
        </div>
      )}

      {status === "ok" && events.length > 0 && (
        <div className="overflow-hidden rounded-lg border">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="px-4 py-2 text-left font-medium">When</th>
                <th className="px-4 py-2 text-left font-medium">Event</th>
                <th className="px-4 py-2 text-left font-medium">IP</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id} className="border-t">
                  <td className="px-4 py-2 text-muted-foreground">{formatDate(e.created_at)}</td>
                  <td className="px-4 py-2">{formatEvent(e.event_type)}</td>
                  <td className="px-4 py-2 font-mono text-xs text-muted-foreground">{e.ip || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
