import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { safeRedirect } from "@/lib/safe-redirect";

/**
 * OAuth callback handler. After the user authenticates with Google /
 * GitHub on Supabase's side, Supabase redirects them to this route with
 * a `?code=...` query param. We exchange the code for a session (which
 * sets the auth cookies), then redirect to wherever they were headed.
 *
 * The `next` query param is set when the auth flow started — typically
 * `/workspace` or the original `redirect` value preserved from the
 * middleware bounce.
 *
 * SECURITY: routes the `next` value through `safeRedirect`, which
 * rejects protocol-relative ("//evil.com"), backslash-variant
 * ("/\\evil.com"), CR/LF-laden, and absolute-URL forms. The original
 * single `startsWith("/")` check happened to be safe today because we
 * prepend `${origin}` and WHATWG URL parses `${origin}//evil.com` as
 * same-origin (NLM's "open redirect" framing was empirically wrong on
 * this point — see project_supabase_auth_security_review_2026-05-16),
 * but a future refactor that drops the `${origin}` prefix would
 * silently re-open the hole. Use the same helper as `/login` so the
 * behavior is consistent and pinned by `safe-redirect.test.mjs`.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");
  const next = searchParams.get("next");

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      const safeNext = safeRedirect(next);
      return NextResponse.redirect(`${origin}${safeNext}`);
    }
  }

  // Failure: send them back to /login with an error flag so the page
  // can show a friendly message instead of just 404ing.
  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`);
}
