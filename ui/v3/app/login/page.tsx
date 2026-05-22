"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { safeRedirect } from "@/lib/safe-redirect";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";
import { Field, OAuthButton } from "@/components/auth/auth-fields";
import { type } from "@/lib/type";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen-safe bg-black" />}>
      <LoginForm />
    </Suspense>
  );
}

function LoginForm() {
  const router = useRouter();
  const params = useSearchParams();
  const { signIn, signInWithGoogle, signInWithGithub } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [oauthBusy, setOauthBusy] = useState<"google" | "github" | null>(null);

  // Bounce destination — preserved across the middleware redirect.
  // safeRedirect rejects absolute URLs / protocol-relative variants so
  // a crafted ?redirect=https://evil.com can't turn a successful sign-in
  // into an off-site bounce.
  const redirect = safeRedirect(params.get("redirect"));

  useEffect(() => {
    if (params.get("error") === "auth_callback_failed") {
      setError("Sign-in didn't complete. Please try again.");
    }
  }, [params]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await signIn(email, password);
      router.push(redirect);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Sign-in failed.");
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
            <h1 className={type.heading.l}>Welcome back</h1>
            <p className="text-sm text-[#1a1a1a]/65">Sign in to your Pebble account.</p>
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
              id="email"
              label="Email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(v) => setEmail(v)}
              placeholder="you@example.com"
            />
            <Field
              id="password"
              label="Password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(v) => setPassword(v)}
              placeholder="Your password"
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

          <p className="text-center text-sm text-[#1a1a1a]/65">
            New to Pebble?{" "}
            <Link href="/signup" className="font-medium text-[#3054ff] hover:underline">
              Create an account
            </Link>
          </p>

          <p className="text-center text-sm text-muted-foreground">
            <Link href="/forgot" className="hover:text-foreground transition-colors">
              Forgot your password?
            </Link>
          </p>

          <p className="text-center text-xs text-[#1a1a1a]/45 leading-relaxed">
            By signing in you agree to our{" "}
            <Link href="/terms"   className="underline hover:text-[#1a1a1a]">Terms</Link>
            {" "}and{" "}
            <Link href="/privacy" className="underline hover:text-[#1a1a1a]">Privacy Policy</Link>.
          </p>
        </MarketingCard>
      </motion.div>
    </MarketingShell>
  );
}
