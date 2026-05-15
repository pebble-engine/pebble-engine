"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, Mail } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

export default function ForgotPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await fetch("/api/auth/forgot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
    } finally {
      setSubmitting(false);
      setSent(true);
    }
  }

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
          {sent ? (
            <div className="text-center space-y-5">
              <div className="w-14 h-14 rounded-full bg-primary/10 text-primary mx-auto flex items-center justify-center">
                <Mail className="w-6 h-6" />
              </div>
              <h1 className="font-display text-3xl font-bold tracking-tight text-foreground">
                Check your inbox.
              </h1>
              <p className="text-muted-foreground">
                If <span className="font-mono text-foreground">{email}</span> is on file, we sent a reset link.
                It expires in an hour.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sm font-medium text-foreground hover:text-primary"
              >
                Back to sign-in <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          ) : (
            <>
              <div className="space-y-2 text-center">
                <h1 className="font-display text-4xl font-bold tracking-tight text-foreground">
                  Reset your password
                </h1>
                <p className="text-muted-foreground">
                  Type the email you signed up with — we&apos;ll send you a one-time link.
                </p>
              </div>

              <form onSubmit={onSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-sm font-medium text-foreground">Email</label>
                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="you@example.com"
                  />
                </div>

                <button
                  type="submit"
                  disabled={submitting || !email.trim()}
                  className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
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

              <p className="text-center text-sm text-muted-foreground">
                Remembered it?{" "}
                <Link href="/login" className="font-medium text-foreground hover:text-primary transition-colors">
                  Sign in
                </Link>
              </p>
            </>
          )}
        </motion.div>
      </main>
    </div>
  );
}
