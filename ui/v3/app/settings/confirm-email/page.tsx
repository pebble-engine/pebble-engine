"use client";

/**
 * /settings/confirm-email — email-change confirmation landing page.
 *
 * The user arrives here by clicking the link we emailed to their NEW
 * address. We immediately call the engine's confirm endpoint with the
 * token from the query string, then show a result card.
 *
 * No auth required — the single-use token IS the auth.
 */

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CheckCircle, XCircle } from "lucide-react";
import { type } from "@/lib/type";

const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");

function ConfirmEmailContent() {
  const params = useSearchParams();
  const token = params?.get("token") || "";
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing confirmation token. Check that you copied the full link from the email.");
      return;
    }
    fetch(
      `${ENGINE_BASE}/api/account/change-email-confirm?token=${encodeURIComponent(token)}`
    )
      .then(async (r) => {
        const body = await r.json().catch(() => ({}));
        if (r.ok) {
          setStatus("ok");
          setMessage((body as { message?: string }).message || "Email updated successfully.");
        } else {
          setStatus("error");
          setMessage(
            (body as { error?: string }).error || "Could not confirm email change. The link may have expired."
          );
        }
      })
      .catch((e: Error) => {
        setStatus("error");
        setMessage("Network error: " + e.message);
      });
  }, [token]);

  return (
    <div className="min-h-screen-safe flex items-center justify-center px-6 py-16 bg-background">
      <div className="max-w-md w-full rounded-2xl border border-border bg-card p-8 text-center space-y-4">
        {status === "loading" ? (
          <>
            <div className="mx-auto w-12 h-12 rounded-full bg-muted animate-pulse" />
            <h1 className={`${type.dashboard.display.s} text-foreground`}>Confirming…</h1>
            <p className={`${type.body.s} text-muted-foreground`}>
              Verifying your confirmation link, just a moment.
            </p>
          </>
        ) : status === "ok" ? (
          <>
            <CheckCircle className="mx-auto w-12 h-12 text-primary" />
            <h1 className={`${type.dashboard.display.s} text-foreground`}>Email updated</h1>
            <p className={`${type.body.s} text-muted-foreground`}>{message}</p>
            <Link
              href="/auth/login"
              className="inline-flex items-center rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              Sign in with your new email
            </Link>
          </>
        ) : (
          <>
            <XCircle className="mx-auto w-12 h-12 text-destructive" />
            <h1 className={`${type.dashboard.display.s} text-foreground`}>Could not confirm</h1>
            <p className={`${type.body.s} text-muted-foreground`}>{message}</p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <Link
                href="/settings"
                className="inline-flex items-center rounded-full bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                Request a new link
              </Link>
              <Link
                href="/dashboard"
                className="text-sm text-muted-foreground hover:text-foreground"
              >
                Back to dashboard
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default function ConfirmEmailPage() {
  return (
    <Suspense fallback={<div className="min-h-screen-safe bg-background" />}>
      <ConfirmEmailContent />
    </Suspense>
  );
}
