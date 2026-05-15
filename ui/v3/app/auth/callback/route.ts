import { NextResponse, type NextRequest } from "next/server";
import { createClient } from "@/lib/supabase/server";

/**
 * OAuth callback handler. After the user authenticates with Google /
 * GitHub on Supabase's side, Supabase redirects them to this route with
 * a `?code=...` query param. We exchange the code for a session (which
 * sets the auth cookies), then redirect to wherever they were headed.
 *
 * The `next` query param is set when the auth flow started — typically
 * `/workspace` or the original `redirect` value preserved from the
 * middleware bounce.
 */
export async function GET(request: NextRequest) {
  const { searchParams, origin } = request.nextUrl;
  const code = searchParams.get("code");
  const next = searchParams.get("next") ?? "/workspace";

  if (code) {
    const supabase = await createClient();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) {
      // Allow same-origin paths only; strip anything starting with a
      // scheme so an attacker can't craft a callback that redirects
      // off-site (?next=https://evil.com).
      const safeNext = next.startsWith("/") ? next : "/workspace";
      return NextResponse.redirect(`${origin}${safeNext}`);
    }
  }

  // Failure: send them back to /login with an error flag so the page
  // can show a friendly message instead of just 404ing.
  return NextResponse.redirect(`${origin}/login?error=auth_callback_failed`);
}
