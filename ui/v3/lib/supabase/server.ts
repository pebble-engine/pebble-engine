import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";

/**
 * Supabase client for server components, route handlers, and server
 * actions. Cookies are read + written through Next.js' request-scoped
 * cookie store so authentication state propagates correctly across
 * SSR + RSC boundaries.
 *
 * Note: server components can't actually set cookies (Next.js will
 * throw). The setAll handler swallows that — middleware is the
 * authoritative place for cookie refresh. See lib/supabase/middleware.ts.
 */
export async function createClient() {
  const cookieStore = await cookies();

  // Same placeholder guard as client.ts — prevents prerender crashes when
  // env vars aren't available at build time.
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL    ?? "https://placeholder.supabase.co",
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "placeholder-anon-key",
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options),
            );
          } catch {
            // Called from a Server Component — Next.js doesn't allow
            // cookie mutation there. The middleware refresh path
            // handles it on the next request.
          }
        },
      },
    },
  );
}
