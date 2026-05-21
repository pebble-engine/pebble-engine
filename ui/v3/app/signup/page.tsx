"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { safeRedirect } from "@/lib/safe-redirect";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";
import { Field, OAuthButton } from "@/components/auth/auth-fields";
import { type } from "@/lib/type";

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black" />}>
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
    } catch (e) {
      setError(e instanceof Error ? e.message : `${provider} sign-in failed.`);
      setOauthBusy(null);
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

            {error && (
              <div role="alert" className="bg-destructive/10 border border-destructive/40 rounded-lg p-3 text-destructive text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={submitting || oauthBusy !== null}
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
