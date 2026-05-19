"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth-provider";
import { safeRedirect } from "@/lib/safe-redirect";
import { MarketingShell, MarketingCard } from "@/components/marketing-shell";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-black" />}>
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
            <h1 className="text-3xl font-semibold tracking-tight">Welcome back</h1>
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

            {error && <p role="alert" className="text-sm text-red-600">{error}</p>}

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

          <p className="text-center text-xs text-[#1a1a1a]/45">
            <Link href="/forgot" className="hover:text-[#1a1a1a] transition-colors">
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

// ---------------------------------------------------------------------------

function Field({
  id, label, type, required, autoComplete, value, onChange, placeholder, minLength,
}: {
  id: string;
  label: string;
  type: string;
  required?: boolean;
  autoComplete?: string;
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
  minLength?: number;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="text-sm font-medium text-[#1a1a1a]">{label}</label>
      <input
        id={id}
        type={type}
        required={required}
        autoComplete={autoComplete}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        minLength={minLength}
        className="w-full rounded-xl border border-stone-200 bg-white px-4 py-3 text-base text-[#1a1a1a] placeholder:text-[#1a1a1a]/35 focus:outline-none focus:ring-2 focus:ring-[#3054ff]/40 focus:border-[#3054ff]"
      />
    </div>
  );
}

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
      className="inline-flex w-full items-center justify-center gap-3 rounded-xl border border-stone-200 bg-stone-50 hover:bg-stone-100 px-5 py-3 text-base font-medium text-[#1a1a1a] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
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

function GithubLogo({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="currentColor">
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.56v-2c-3.2.7-3.87-1.36-3.87-1.36-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.69 1.25 3.34.96.1-.74.4-1.25.73-1.54-2.55-.29-5.23-1.27-5.23-5.65 0-1.25.45-2.27 1.18-3.07-.12-.29-.51-1.46.11-3.04 0 0 .96-.31 3.15 1.17a10.95 10.95 0 0 1 5.74 0c2.18-1.48 3.14-1.17 3.14-1.17.63 1.58.23 2.75.11 3.04.74.8 1.18 1.82 1.18 3.07 0 4.39-2.69 5.35-5.25 5.64.41.35.77 1.05.77 2.12v3.14c0 .31.21.67.8.56A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z"/>
    </svg>
  );
}
