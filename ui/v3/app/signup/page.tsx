"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2, Mail } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { safeRedirect } from "@/lib/safe-redirect";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";
import { Field, OAuthButton } from "@/components/auth/auth-fields";
import { TurnstileWidget } from "@/components/turnstile-widget";
import { type } from "@/lib/type";

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen-safe bg-black" />}>
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
  const [done, setDone] = useState(false);
  // 2026-05-24 — Turnstile token + disposable-email gate. The widget
  // pumps a fresh token in via onToken; we POST it to
  // /api/auth/precheck right before calling Supabase signUp. Without
  // a token the submit button stays disabled. The DEV_BYPASS sentinel
  // unlocks the form when NEXT_PUBLIC_TURNSTILE_SITE_KEY isn't set.
  const [turnstileToken, setTurnstileToken] = useState<string | null>(null);

  const redirect = safeRedirect(params.get("redirect"));
  const inviteCode = params.get("invite");

  // Beta invite — persist for build API header (see docs/BETA_INVITE.md).
  if (typeof window !== "undefined" && inviteCode) {
    try {
      localStorage.setItem("pebble_invite_code", inviteCode.trim());
    } catch { /* private mode */ }
  }

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
    if (!turnstileToken) {
      setError("Please complete the verification challenge.");
      return;
    }
    setSubmitting(true);
    try {
      // 2026-05-24 — server-side gate: Turnstile + disposable email.
      // Runs BEFORE Supabase signup so a bot's email never reaches
      // Supabase Auth (no half-created accounts, no confirmation
      // email spend on doomed signups).
      const precheckResp = await fetch("/api/auth/precheck", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ token: turnstileToken, email: email.trim() }),
      });
      const precheck = (await precheckResp.json()) as { ok: boolean; reason?: string };
      if (!precheck.ok) {
        setError(precheck.reason || "Verification failed. Please try again.");
        setSubmitting(false);
        return;
      }
      await signUp(email, password, firstName.trim() || undefined);
      setDone(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-up failed.");
    } finally {
      // Reset in finally so a stuck-or-cancelled flow never leaves
      // the button locked in "Creating account…". setState on an
      // unmounting component is a harmless no-op in React 19.
      setSubmitting(false);
    }
  }

  async function onOAuth(provider: "google" | "github") {
    setError(null);
    setOauthBusy(provider);
    try {
      if (provider === "google") await signInWithGoogle();
      else await signInWithGithub();
    } catch (e) {
      setError(e instanceof Error ? e.message : `${provider} sign-in failed.`);
    } finally {
      // Same reasoning as the login page — never let the OAuth button
      // stay disabled if the provider redirect is blocked or slow.
      setOauthBusy(null);
    }
  }

  if (done) {
    return (
      <MarketingShell>
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="w-full max-w-md"
        >
          <MarketingCard>
            <div className="flex flex-col items-center text-center space-y-4 py-4">
              <div className="w-14 h-14 rounded-full bg-[#3054ff]/10 flex items-center justify-center">
                <Mail className="w-7 h-7 text-[#3054ff]" />
              </div>
              <h1 className="text-xl font-bold text-[#1a1a1a]">Check your inbox</h1>
              <p className="text-sm text-[#1a1a1a]/65 leading-relaxed">
                We sent a confirmation link to <strong className="text-[#1a1a1a]">{email}</strong>.
                Click it to activate your account and start building.
              </p>
              <p className="text-xs text-[#1a1a1a]/45">
                Didn&apos;t get it? Check your spam folder or{" "}
                <button
                  type="button"
                  onClick={() => setDone(false)}
                  className="underline hover:text-[#1a1a1a] transition-colors"
                >
                  try again
                </button>.
              </p>
              <Link
                href="/login"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-[#3054ff] hover:underline"
              >
                Back to sign in <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </MarketingCard>
        </motion.div>
      </MarketingShell>
    );
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
          <div className="space-y-2 text-center">
            <h1 className={type.heading.l}>Create your account</h1>
            <p className="text-sm text-[#1a1a1a]/65">
              Start building for free. No card required.
            </p>
          </div>

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

          <div className="flex items-center gap-3 text-xs uppercase tracking-widest text-[#1a1a1a]/45">
            <span className="h-px flex-1 bg-stone-200" />
            or with email
            <span className="h-px flex-1 bg-stone-200" />
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <Field
              id="first-name"
              label="First name"
              type="text"
              autoComplete="given-name"
              value={firstName}
              onChange={setFirstName}
              placeholder="What should we call you?"
            />
            <Field
              id="email"
              label="Email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={setEmail}
              placeholder="you@example.com"
            />
            <Field
              id="password"
              label="Password"
              type="password"
              required
              autoComplete="new-password"
              value={password}
              onChange={setPassword}
              placeholder="At least 8 characters"
              minLength={8}
            />
            <Field
              id="confirm"
              label="Confirm password"
              type="password"
              required
              autoComplete="new-password"
              value={confirm}
              onChange={setConfirm}
              placeholder="Type it again"
              minLength={8}
            />

            {/* Cloudflare Turnstile — invisible CAPTCHA. Pumps a
                short-lived token via onToken; the submit handler
                ships it to /api/auth/precheck. In dev (no site key
                in .env) the widget fires DEV_BYPASS immediately so
                the form is usable without Cloudflare wiring. */}
            <TurnstileWidget onToken={setTurnstileToken} />

            {error && (
              <div role="alert" className="bg-destructive/10 border border-destructive/40 rounded-lg p-3 text-destructive text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || oauthBusy !== null || !turnstileToken}
              className="group inline-flex w-full items-center justify-center gap-2 rounded-full bg-[#3054ff] hover:bg-[#2040e0] px-6 py-3 text-base font-medium text-white transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
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

          <p className="text-center text-sm text-[#1a1a1a]/65">
            Already have an account?{" "}
            <Link
              href={redirect !== "/workspace" ? `/login?redirect=${encodeURIComponent(redirect)}` : "/login"}
              className="font-medium text-[#3054ff] hover:underline"
            >
              Sign in
            </Link>
          </p>

          <p className="text-center text-xs text-[#1a1a1a]/45 leading-relaxed">
            Auth is handled by Supabase — your password is hashed; we never see it in plaintext.
            <br />
            By signing up you agree to our{" "}
            <Link href="/terms"   className="underline hover:text-[#1a1a1a]">Terms</Link>
            {" "}and{" "}
            <Link href="/privacy" className="underline hover:text-[#1a1a1a]">Privacy Policy</Link>.
          </p>
        </MarketingCard>
      </motion.div>
    </MarketingShell>
  );
}
