"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, ShieldCheck } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";

/**
 * Password reset confirm. The user arrives here by clicking the link
 * Supabase emailed after `/forgot`. Supabase's URL contains a hash
 * fragment with the recovery tokens; the browser client auto-detects
 * it on mount and creates a short-lived session. Once that session
 * exists, we can call `supabase.auth.updateUser({ password })`.
 */
export default function ResetPage() {
  return (
    <MarketingShell>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md"
      >
        <MarketingCard>
          <ResetForm />
        </MarketingCard>
      </motion.div>
    </MarketingShell>
  );
}

function ResetForm() {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [ready, setReady] = useState<"checking" | "ok" | "no-session">("checking");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) return;
      setReady(data.session ? "ok" : "no-session");
    });
    const { data: sub } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") setReady("ok");
    });
    return () => {
      cancelled = true;
      sub.subscription.unsubscribe();
    };
  }, [supabase]);

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
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        setError(error.message);
        setSubmitting(false);
        return;
      }
      router.push("/workspace");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed.");
      setSubmitting(false);
    }
  }

  if (ready === "checking") {
    return <p className="text-[#1a1a1a]/55 text-center text-sm">Loading reset link…</p>;
  }

  if (ready === "no-session") {
    return (
      <div className="text-center space-y-4">
        <h1 className="text-2xl font-semibold">Reset link expired or already used.</h1>
        <p className="text-sm text-[#1a1a1a]/65">
          Open the link from your latest reset email, or request a new one.
        </p>
        <Link
          href="/forgot"
          className="inline-flex items-center gap-2 text-sm font-medium text-[#3054ff] hover:underline"
        >
          Request a new link <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-2 text-center">
        <div className="w-14 h-14 rounded-full bg-[#3054ff]/10 text-[#3054ff] mx-auto flex items-center justify-center mb-3">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <h1 className="text-3xl font-semibold tracking-tight">Pick a new password</h1>
        <p className="text-sm text-[#1a1a1a]/65">
          At least 8 characters. After saving, we&apos;ll sign you in.
        </p>
      </div>

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="password" className="text-sm font-medium text-[#1a1a1a]">New password</label>
          <input
            id="password"
            type="password"
            required
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="At least 8 characters"
            className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-base text-[#1a1a1a] placeholder:text-[#1a1a1a]/35 focus:outline-none focus:ring-2 focus:ring-[#3054ff]/40 focus:border-[#3054ff]"
          />
        </div>

        <div className="space-y-1.5">
          <label htmlFor="confirm" className="text-sm font-medium text-[#1a1a1a]">Confirm</label>
          <input
            id="confirm"
            type="password"
            required
            autoComplete="new-password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="Same one again"
            className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-base text-[#1a1a1a] placeholder:text-[#1a1a1a]/35 focus:outline-none focus:ring-2 focus:ring-[#3054ff]/40 focus:border-[#3054ff]"
          />
        </div>

        {error && <p role="alert" className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-[#3054ff] hover:bg-[#2040e0] px-6 py-3 text-base font-medium text-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
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
