import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

/**
 * Middleware helper that refreshes the Supabase auth cookie on every
 * request and gates protected routes. Called from the project-root
 * `middleware.ts`.
 *
 * Routes gated by this function:
 * - `/workspace` and any sub-path → must be signed in. Unauthenticated
 *   users get bounced to /login with `?redirect=/workspace#phase=…`.
 * - `/dashboard` → same treatment (it lists the user's projects).
 *
 * Public routes (no gate): `/`, `/landing`, `/login`, `/signup`,
 * `/forgot`, `/reset`, `/migrate`, `/help`, `/auth/callback`, plus
 * `/preview/*` (which streams generated-site HTML from the engine —
 * we want shared preview links to work without forcing the visitor
 * to sign up).
 */
export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          supabaseResponse = NextResponse.next({ request });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // IMPORTANT: getUser() (not getSession()) — getSession can return a
  // session from a tampered cookie. getUser() forces a re-validation
  // against Supabase Auth, which is what we want at the protection
  // boundary.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const path = request.nextUrl.pathname;
  const isProtected =
    path.startsWith("/workspace") || path.startsWith("/dashboard");

  if (!user && isProtected) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    // Preserve where they were heading so we can bounce them back
    // after sign-in (including hash for workspace phase).
    url.searchParams.set("redirect", path + (request.nextUrl.hash || ""));
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
