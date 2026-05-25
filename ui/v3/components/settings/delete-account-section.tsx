"use client";

/**
 * DeleteAccountSection — extracted verbatim from settings/page.tsx (A3).
 * Shows deletion-scheduled banner + cancel button, or the delete form
 * (collapsible, requires email-typed confirmation, 14-day cooling-off).
 */

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, ChevronDown } from "lucide-react";
import { type } from "@/lib/type";
import { useAuth } from "@/components/auth-provider";
import { createClient } from "@/lib/supabase/client";

// ── component ─────────────────────────────────────────────────────────────────

export function DeleteAccountSection() {
  const router = useRouter();
  const { user } = useAuth();
  const supabase = useMemo(() => createClient(), []);

  // ── deletion state ─────────────────────────────────────────────────────────
  const [deletionScheduled, setDeletionScheduled] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm]         = useState("");
  const [deleteSubmitting, setDeleteSubmitting]   = useState(false);
  const [deleteError, setDeleteError]             = useState<string | null>(null);
  const [cancelSubmitting, setCancelSubmitting]   = useState(false);
  const [showDeleteZone, setShowDeleteZone]       = useState(false);

  const deletionDate = deletionScheduled ? deletionScheduled.slice(0, 10) : null;

  // ── hydrate from server on mount ───────────────────────────────────────────
  // /api/account/profile returns `deletion_scheduled_for: string | null`
  // (verified in pebble/server/account.py:354). Without this, a user who
  // schedules deletion, closes the tab, then comes back sees the delete
  // form with no banner — the 14-day undo affordance is invisible.
  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    (async () => {
      try {
        const { data: session } = await supabase.auth.getSession();
        const token = session?.session?.access_token;
        if (!token) return;
        const res = await fetch("/api/account/profile", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) return;
        const body = (await res.json()) as { deletion_scheduled_for: string | null };
        if (!cancelled && body.deletion_scheduled_for) {
          setDeletionScheduled(body.deletion_scheduled_for);
        }
      } catch {
        // non-fatal — worst case the user re-attempts deletion and the
        // backend tells them one is already scheduled.
      }
    })();
    return () => { cancelled = true; };
  }, [user, supabase]);

  // ── handlers ───────────────────────────────────────────────────────────────

  async function onRequestDeletion() {
    setDeleteError(null);
    if (deleteConfirm.trim().toLowerCase() !== (user?.email ?? "").toLowerCase()) {
      setDeleteError("Email doesn't match. Type your email address to confirm.");
      return;
    }
    setDeleteSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) { setDeleteError("Not authenticated."); return; }
      const res = await fetch("/api/account/delete", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const body = await res.json().catch(() => ({}));
      if (body.deleted) {
        await supabase.auth.signOut();
        router.replace("/landing");
        return;
      }
      if (body.scheduled_for) setDeletionScheduled(body.scheduled_for);
      setDeleteConfirm("");
    } catch (err) {
      setDeleteError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setDeleteSubmitting(false);
    }
  }

  async function onCancelDeletion() {
    setCancelSubmitting(true);
    try {
      const { data: session } = await supabase.auth.getSession();
      const token = session?.session?.access_token;
      if (!token) return;
      await fetch("/api/account/cancel-deletion", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setDeletionScheduled(null);
    } catch {
      // non-fatal
    } finally {
      setCancelSubmitting(false);
    }
  }

  if (!user) return null;

  return (
    <div className="space-y-4">
      <div>
        <h2 className="mb-1 text-lg font-medium text-destructive">Delete account</h2>
        <p className={`${type.body.s} text-muted-foreground`}>
          Permanently remove your account and all associated data.
        </p>
      </div>

      {/* Deletion scheduled banner */}
      {deletionDate && (
        <div className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4">
          <AlertTriangle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
          <div className="flex-1 space-y-2">
            <p className={`${type.body.s} text-destructive font-medium`}>
              Account scheduled for deletion on {deletionDate}
            </p>
            <p className={`${type.body.s} text-muted-foreground`}>
              All your sites and data will be permanently removed. You can cancel this before that date.
            </p>
            <button
              type="button"
              onClick={onCancelDeletion}
              disabled={cancelSubmitting}
              className="text-sm font-medium text-primary hover:underline disabled:opacity-50"
            >
              {cancelSubmitting ? "Cancelling…" : "Cancel deletion"}
            </button>
          </div>
        </div>
      )}

      {/* Delete account form (only shown when no deletion is scheduled) */}
      {!deletionDate && (
        <div>
          <button
            type="button"
            onClick={() => setShowDeleteZone(v => !v)}
            className={`flex items-center gap-1.5 ${type.body.s} text-destructive hover:underline`}
          >
            Delete my account
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showDeleteZone ? "rotate-180" : ""}`} />
          </button>
          <AnimatePresence>
            {showDeleteZone && (
              <motion.div
                key="delete-zone"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-4 p-4 rounded-xl border border-destructive/40 bg-destructive/5 space-y-3">
                  <p className={`${type.body.s} text-muted-foreground`}>
                    Type your email address to confirm. Your account will enter a{" "}
                    <strong>14-day cooling-off period</strong> — you can cancel anytime before it expires.
                    After that, all your data is permanently deleted.
                  </p>
                  <label className="block">
                    <span className={`${type.label} text-muted-foreground`}>{user.email}</span>
                    <input
                      type="email"
                      value={deleteConfirm}
                      onChange={(e) => setDeleteConfirm(e.target.value)}
                      placeholder={user.email ?? ""}
                      autoComplete="off"
                      className="mt-1 w-full rounded-lg border border-destructive/40 bg-background px-3 py-2 text-foreground focus:outline-none focus:ring-2 focus:ring-destructive"
                    />
                  </label>
                  {deleteError && (
                    <p className={`${type.body.s} text-destructive`} role="alert">{deleteError}</p>
                  )}
                  <button
                    type="button"
                    onClick={onRequestDeletion}
                    disabled={deleteSubmitting || deleteConfirm.trim() === ""}
                    className="inline-flex items-center rounded-full bg-destructive px-4 py-2 text-sm font-semibold text-white hover:bg-destructive/90 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {deleteSubmitting ? "Scheduling…" : "Schedule account deletion"}
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}
