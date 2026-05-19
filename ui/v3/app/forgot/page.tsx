"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, Mail } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";

export default function ForgotPage() {
  const supabase = useMemo(() => createClient(), []);
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      // Don't surface "no such email" errors back to the user — they
      // become an enumeration oracle. Show the same "check your inbox"
      // state regardless.
      await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset`,
      });
    } finally {
      setSubmitting(false);
      setSent(true);
    }
  }

  return (
    <MarketingShell>
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md"
      >
        <MarketingCard>
          {sent ? (
            <div className="text-center space-y-5">
              <div className="w-14 h-14 rounded-full bg-[#3054ff]/10 text-[#3054ff] mx-auto flex items-center justify-center">
                <Mail className="w-6 h-6" />
              </div>
              <h1 className="text-3xl font-semibold tracking-tight">Check your inbox.</h1>
              <p className="text-sm text-[#1a1a1a]/65">
                If <span className="font-mono text-[#1a1a1a]">{email}</span> is on file, we sent a reset link.
                It expires in an hour.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sm font-medium text-[#3054ff] hover:underline"
              >
                Back to sign-in <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <>
              <div className="space-y-2 text-center">
                <h1 className="text-3xl font-semibold tracking-tight">Reset your password</h1>
                <p className="text-sm text-[#1a1a1a]/65">
                  Type the email you signed up with — we&apos;ll send you a one-time link.
                </p>
              </div>

              <form onSubmit={onSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-sm font-medium text-[#1a1a1a]">Email</label>
                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-base text-[#1a1a1a] placeholder:text-[#1a1a1a]/35 focus:outline-none focus:ring-2 focus:ring-[#3054ff]/40 focus:border-[#3054ff]"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting || !email.trim()}
                  className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-[#3054ff] hover:bg-[#2040e0] px-6 py-3 text-base font-medium text-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" /> Sending…
                    </>
                  ) : (
                    <>
                      Send reset link
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                    </>
                  )}
                </button>
              </form>

              <p className="text-center text-sm text-[#1a1a1a]/65">
                Remembered it?{" "}
                <Link href="/login" className="font-medium text-[#3054ff] hover:underline">
                  Sign in
                </Link>
              </p>
            </>
          )}
        </MarketingCard>
      </motion.div>
    </MarketingShell>
  );
}
