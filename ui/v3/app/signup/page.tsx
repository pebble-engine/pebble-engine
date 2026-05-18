"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import { safeRedirect } from "@/lib/safe-redirect";

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-background" />}>
      <SignupForm />
    </Suspense>
  );
}

function SignupForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { signUp, signInWithGoogle, signInWithGithub } = useAuth();
  const [firstName, setFirstName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [oauthBusy, setOauthBusy] = useState<"google" | "github" | null>(null);

  const redirect = safeRedirect(params.get("redirect"));

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
      await signUp(email, password, firstName.trim() || undefined);
      router.push(redirect);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-up failed.");
      setSubmitting(false);
    }
  }

  async function onOAuth(provider: "google" | "github") {
    setError(null);
    setOauthBusy(provider);
    try {
      if (provider === "google") await signInWithGoogle();
      else await signInWithGithub();
      // The browser is now navigating to the provider — no state to reset.
    } catch (e) {
      setError(e instanceof Error ? e.message : `${provider} sign-in failed.`);
      setOauthBusy(null);
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
          className="w-full max-w-md space-y-6"
        >
          <div className="space-y-2 text-center">
            <h1 className="font-display text-4xl font-bold tracking-tight text-foreground">
              Create your account
            </h1>
            <p className="text-muted-foreground">
              Start building for free. No card required.
            </p>
          </div>

          {/* OAuth — primary path for most users, so it's on top */}
          <div className="space-y-2">
            <OAuthButton
              provider="google"
              busy={oauthBusy === "google"}
              disabled={oauthBusy !== null}
              onClick={() => onOAuth("google")}
            />
            <OAuthButton
              provider="github"
              busy={oauthBusy === "github"}
              disabled={oauthBusy !== null}
              onClick={() => onOAuth("github")}
            />
          </div>

          <div className="flex items-center gap-3 text-xs uppercase tracking-widest text-muted-foreground">
            <span className="h-px flex-1 bg-border" />
            or with email
            <span className="h-px flex-1 bg-border" />
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label htmlFor="first-name" className="text-sm font-medium text-foreground">First name</label>
              <input
                id="first-name"
                type="text"
                autoComplete="given-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="What should we call you?"
              />
            </div>

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
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="At least 8 characters"
                minLength={8}
              />
            </div>

            <div className="space-y-1.5">
              <label htmlFor="confirm" className="text-sm font-medium text-foreground">Confirm password</label>
              <input
                id="confirm"
                type="password"
                required
                autoComplete="new-password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="w-full rounded-xl border border-border bg-card px-4 py-3 text-base text-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="Type it again"
                minLength={8}
              />
            </div>

            {error && (
              <p role="alert" className="text-sm text-destructive">{error}</p>
            )}

            <button
              type="submit"
              disabled={submitting || oauthBusy !== null}
              className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-primary px-6 py-3.5 text-base font-medium text-primary-foreground shadow-[var(--shadow-1)] transition-transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {submitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" /> Creating account…
                </>
              ) : (
                <>
                  Create account
                  <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
                </>
              )}
            </button>
          </form>

          <p className="text-center text-sm text-muted-foreground">
            Already have an account?{" "}
            <Link
              href={redirect !== "/workspace" ? `/login?redirect=${encodeURIComponent(redirect)}` : "/login"}
              className="font-medium text-foreground hover:text-primary transition-colors"
            >
              Sign in
            </Link>
          </p>

          <p className="text-center text-xs text-muted-foreground">
            Auth is handled by Supabase — your password is hashed; we never see it in plaintext.
            <br />
            By signing up you agree to our{" "}
            <Link href="/terms" className="underline hover:text-foreground transition-colors">Terms</Link>
            {" "}and{" "}
            <Link href="/privacy" className="underline hover:text-foreground transition-colors">Privacy Policy</Link>.
          </p>
        </motion.div>
      </main>
    </div>
  );
}

// ---------------------------------------------------------------------------

function OAuthButton({
  provider, busy, disabled, onClick,
}: {
  provider: "google" | "github";
  busy: boolean;
  disabled: boolean;
  onClick: () => void;
}) {
  const label = provider === "google" ? "Continue with Google" : "Continue with GitHub";
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex w-full items-center justify-center gap-3 rounded-xl border border-border bg-card px-5 py-3 text-base font-medium text-foreground transition-colors hover:bg-accent disabled:opacity-60 disabled:cursor-not-allowed"
    >
      {busy ? (
        <Loader2 className="h-5 w-5 animate-spin" />
      ) : provider === "google" ? (
        <GoogleLogo className="h-5 w-5" />
      ) : (
        <GithubLogo className="h-5 w-5" />
      )}
      {label}
    </button>
  );
}

// Inline GitHub mark — Lucide dropped its Github icon in v1.x. Pulled
// from GitHub's brand toolkit (Octocat-less monochrome mark).
function GithubLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="currentColor">
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.87-1.36-3.87-1.36-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.69 1.25 3.34.96.1-.74.4-1.25.73-1.54-2.55-.29-5.23-1.27-5.23-5.65 0-1.25.45-2.27 1.18-3.07-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.15 1.17a10.95 10.95 0 0 1 5.74 0c2.18-1.48 3.14-1.17 3.14-1.17.63 1.58.23 2.75.11 3.04.74.8 1.18 1.82 1.18 3.07 0 4.39-2.69 5.35-5.25 5.64.41.35.77 1.05.77 2.12v3.14c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>
    </svg>
  );
}

// Inline Google logo — Lucide doesn't ship one, and the official multi-
// colour glyph is recognisable enough that a monochrome fallback would
// undersell the brand. Pulled from Google's brand guide ("G"-mark).
function GoogleLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.76h3.56c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.56-2.76c-.98.66-2.24 1.06-3.72 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.11A6.58 6.58 0 0 1 5.48 12c0-.73.13-1.45.36-2.11V7.05H2.18A11 11 0 0 0 1 12c0 1.78.42 3.47 1.18 4.95l3.66-2.84z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1A11 11 0 0 0 2.18 7.05l3.66 2.84C6.71 7.3 9.14 5.38 12 5.38z"/>
    </svg>
  );
}
