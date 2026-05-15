"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { useAuth } from "@/components/auth-provider";

function ResetForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { refresh } = useAuth();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords don't match.");
      return;
    }
    setSubmitting(true);
    try {
      const resp = await fetch("/api/auth/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, password }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        setError(data.error || "Reset failed.");
        setSubmitting(false);
        return;
      }
      // Server set our cookie — refresh auth state and go home.
      try { await refresh(); } catch {}
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed.");
      setSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="text-center space-y-4">
        <p className="font-display text-2xl text-foreground">No reset token.</p>
        <p className="text-muted-foreground">
          Open the link from your reset email, or request a new one.
        </p>
        <Link href="/forgot" className="inline-flex items-center gap-2 text-sm font-medium text-foreground hover:text-primary">
          Request a new link <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-2 text-center">
        <div className="w-14 h-14 rounded-full bg-primary/10 text-primary mx-auto flex items-center justify-center mb-3">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h1 className="font-display text-4xl font-bold tracking-tight text-foreground">
          Pick a new password
        </h1>
        <p className="text-muted-foreground">
          At least 8 characters. After saving, we&apos;ll sign you back in.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="password" className="text-sm font-medium text-foreground">New password</label>
          <input
            id="password"
            type="password"
            required
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="At least 8 characters"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="confirm" className="text-sm font-medium text-foreground">Confirm</label>
          <input
            id="confirm"
            type="password"
            required
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Same one again"
          />
        </div>

        {error && <p role="alert" className="text-sm text-destructive">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Saving…
            </>
          ) : (
            <>
              Save new password
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </button>
      </form>
    </>
  );
}

export default function ResetPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="flex items-center justify-between px-6 py-5">
        <Link href="/landing" className="font-display text-2xl font-bold tracking-tight text-foreground">
          Pebble.
        </Link>
        <ThemeToggle />
      </header>

      <main className="flex-1 flex items-center justify-center px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-md space-y-7"
        >
          <Suspense fallback={<p className="text-muted-foreground text-center">Loading…</p>}>
            <ResetForm />
          </Suspense>
        </motion.div>
      </main>
    </div>
  );
}
