"use client";

import { createBrowserClient } from "@supabase/ssr";

/**
 * Supabase client for the browser. Use this in client components for
 * sign-in, sign-out, and any user-scoped reads/writes that originate
 * from interactive UI. The auth state is mirrored into HttpOnly cookies
 * managed by the @supabase/ssr middleware so SSR pages can read it.
 */
export function createClient() {
  // NEXT_PUBLIC_ vars are baked into the bundle at build time. If they're
  // absent (e.g. Vercel build before env vars are set, or local dev without
  // .env.local), createBrowserClient throws and breaks prerendering.
  // Fall back to placeholder strings so the build succeeds; auth simply
  // returns null user until the real keys are deployed.
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL    ?? "https://placeholder.supabase.co",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "placeholder-anon-key",
  );
}
