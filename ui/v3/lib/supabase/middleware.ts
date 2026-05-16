import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";

/**
 * Middleware helper that refreshes the Supabase auth cookie on every
 * request and gates protected routes. Called from the project-root
 * `proxy.ts`.
 *
 * ROUTE AUDIT (kept in sync with `ui/v3/app/**`):
 *
 *  Gated (must be signed in — listed in PROTECTED_PREFIXES below):
 *    /workspace*    user's active build/edit session
 *    /dashboard*    list of the user's projects
 *    /admin*        engine-side admin (further gated by PEBBLE_ADMIN_EMAIL)
 *    /inbox*        per-project form submissions (further gated by
 *                   require_project_owner on the engine side)
 *    /thinking      legacy client-redirect into /workspace#phase=idea —
 *                   gated so a JS-disabled visitor can't see the
 *                   layout shell (defense in depth)
 *    /plan-review   legacy client-redirect into /workspace#phase=plan
 *    /publish       legacy client-redirect into /workspace#phase=publish
 *
 *  Public (no gate):
 *    /              welcome / marketing root
 *    /landing       marketing
 *    /login         /signup /forgot /reset auth flows
 *    /auth/callback OAuth post-flow
 *    /migrate       URL-extraction scanner (logged-out-friendly)
 *    /help          plain FAQ
 *    /intake        questionnaire (designed for logged-out fill, auth
 *                   only required at /api/generate)
 *    /preview/*     engine-proxied generated-site HTML; we want shared
 *                   preview links to work without forcing signup
 *
 * SECURITY POSTURE: this is the fail-open form (explicit-allowlist of
 * gated routes). The 2026-05-16 NLM pass flagged that adding a new
 * protected page requires updating PROTECTED_PREFIXES, and forgetting
 * leaves it publicly readable. Deny-by-default with an explicit public
 * list would be safer but requires a broader audit. For now the trade-
 * off is documented and pinned by `tests/test_route_gating.py`.
 */
const PROTECTED_PREFIXES = [
  "/workspace",
  "/dashboard",
  "/admin",
  "/inbox",
  // Legacy client-side redirects into /workspace. These render null
  // and rely on a JS-driven router.replace() to land the visitor on
  // the gated phase. With JS disabled or HTML scraped, the empty
  // shell is harmless TODAY, but adding any rendered content later
  // would leak it. Gate them at the middleware to remove the
  // ambiguity (NLM round-three pass, 2026-05-16).
  "/thinking",
  "/plan-review",
  "/publish",
] as const;

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
  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    path === prefix || path.startsWith(prefix + "/"),
  );

  if (!user && isProtected) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    // Preserve where they were heading so we can bounce them back
    // after sign-in (including hash for workspace phase). The path
    // comes from `request.nextUrl.pathname` and ALWAYS starts with
    // "/", so the redirect value always begins safely. The hash piece
    // is attacker-controllable in theory, but safeRedirect on the
    // consumption side (login page, /auth/callback) treats it as
    // opaque: the whole value is either passed through verbatim
    // (`/workspace#phase=plan` → `/workspace#phase=plan`) or rejected
    // entirely back to /workspace (control chars anywhere, or
    // authority shift at position 1 — `//evil.com`, `/\\evil.com`).
    // A hash fragment cannot shift origin via router.push, so a
    // crafted `#//evil.com` just sets the URL hash on /workspace.
    url.searchParams.set("redirect", path + (request.nextUrl.hash || ""));
    return NextResponse.redirect(url);
  }

  return supabaseResponse;
}
