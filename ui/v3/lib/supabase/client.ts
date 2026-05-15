"use client";

import { createBrowserClient } from "@supabase/ssr";

/**
 * Supabase client for the browser. Use this in client components for
 * sign-in, sign-out, and any user-scoped reads/writes that originate
 * from interactive UI. The auth state is mirrored into HttpOnly cookies
 * managed by the @supabase/ssr middleware so SSR pages can read it.
 */
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
