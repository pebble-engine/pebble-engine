"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { ThemeToggle } from "@/components/theme-toggle";

export default function LoginPage() {
  const router = useRouter();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signIn(email, password);
      router.push("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-in failed.");
      setSubmitting(false);
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
          <div className="space-y-2 text-center">
            <h1 className="font-display text-4xl font-bold tracking-tight text-foreground">
              Welcome back
            </h1>
            <p className="text-muted-foreground">Sign in to your Pebble account.</p>
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

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-sm font-medium text-foreground">Password</label>
              <input
                id="password"
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Your password"
              />
            </div>

            {error && (
              <p role="alert" className="text-sm text-destructive">{error}</p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Signing in…
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            New to Pebble?{" "}
            <Link href="/signup" className="font-medium text-foreground hover:text-primary transition-colors">
              Create an account
            </Link>
          </p>
        </motion.div>
      </main>
    </div>
  );
}
