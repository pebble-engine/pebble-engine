/**
 * /api/auth/precheck — Cloudflare Turnstile + disposable-email gate
 * before Supabase signup (2026-05-24).
 *
 * Marc 2026-05-24 security review: bot signup attacks are the biggest
 * cost-burning vector. Two cheap defenses bundled here, both run
 * server-side BEFORE Supabase ever sees the request:
 *
 *   1. Turnstile token verification via Cloudflare's siteverify API.
 *      Invisible CAPTCHA, blocks ~95% of headless-browser bots.
 *   2. Disposable-email domain check. ~70 throwaway providers blocked
 *      (mailinator, 10minutemail, yopmail, etc.).
 *
 * v3 signup form calls this route, waits for {ok: true}, then proceeds
 * with the Supabase client-side signUp() call. On {ok: false}, the
 * form shows the returned `reason` to the user and never touches
 * Supabase — so failed bot attempts never create a half-account or
 * cost a confirmation email send.
 *
 * Failure modes:
 *   - TURNSTILE_SECRET_KEY missing: route returns 500 with a
 *     pebble-side error log. Signup still works (signUp falls back
 *     to no precheck) — but the BOT FLOODGATE IS OPEN. So in prod
 *     this misconfig is a P0.
 *   - Cloudflare siteverify down: 503 from our route. Form should
 *     surface "Verification system unavailable, try again in a
 *     moment." This is the right policy — if we can't verify the
 *     token, we shouldn't let through.
 */

import { NextRequest, NextResponse } from "next/server";
import { isDisposableEmail } from "@/lib/disposable-emails";

const TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify";

type TurnstileVerifyResponse = {
  success: boolean;
  "error-codes"?: string[];
  challenge_ts?: string;
  hostname?: string;
  action?: string;
};

export async function POST(req: NextRequest) {
  let body: { token?: unknown; email?: unknown };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ ok: false, reason: "Invalid request body." }, { status: 400 });
  }

  const token = typeof body.token === "string" ? body.token : "";
  const email = typeof body.email === "string" ? body.email.trim() : "";

  // Local dev: widget sends DEV_BYPASS when hostname is localhost (Turnstile
  // keys are bound to pebbleapp.ai). Accept before siteverify.
  if (process.env.NODE_ENV !== "production" && token === "DEV_BYPASS") {
    if (email && isDisposableEmail(email)) {
      return NextResponse.json(
        {
          ok: false,
          reason: "Please use a permanent email address. Throwaway providers aren't supported.",
        },
        { status: 400 },
      );
    }
    return NextResponse.json({ ok: true, fallback: "dev_bypass" });
  }

  // Disposable-email check first — cheap, no network call, blocks
  // before we burn a Cloudflare siteverify request on a doomed signup.
  if (email && isDisposableEmail(email)) {
    return NextResponse.json(
      {
        ok: false,
        reason: "Please use a permanent email address. Throwaway providers aren't supported.",
      },
      { status: 400 },
    );
  }

  // Turnstile verify. We deliberately accept signups even when the
  // SECRET key isn't set — that's only legal in dev. In prod the key
  // is set and we always require a valid token.
  const secret = (process.env.TURNSTILE_SECRET_KEY || "").trim();
  if (!secret) {
    // 2026-05-24 security smoke I6: in production this is a P0 misconfig
    // (signup gate open to bots). Fail-closed with 503 so the issue is
    // loud + observable in Sentry. In dev we keep the bypass so local
    // signup flow works without Cloudflare wiring.
    if (process.env.NODE_ENV === "production") {
      console.error("[precheck] PROD: TURNSTILE_SECRET_KEY missing — refusing signups");
      return NextResponse.json(
        { ok: false, reason: "Verification system unavailable. Please try again in a moment." },
        { status: 503 },
      );
    }
    console.warn("[precheck] TURNSTILE_SECRET_KEY not set — skipping verify (dev fallback)");
    return NextResponse.json({ ok: true, fallback: "no_turnstile_configured" });
  }

  if (!token) {
    return NextResponse.json(
      { ok: false, reason: "Verification required. Please complete the challenge and try again." },
      { status: 400 },
    );
  }

  // Forward the remote IP so Cloudflare can correlate with their
  // own per-IP scoring. Edge environments expose this differently;
  // x-forwarded-for is the common case behind Vercel + Cloudflare.
  const remoteIp =
    req.headers.get("cf-connecting-ip") ||
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    "";

  const form = new URLSearchParams();
  form.append("secret", secret);
  form.append("response", token);
  if (remoteIp) form.append("remoteip", remoteIp);

  let verifyJson: TurnstileVerifyResponse;
  try {
    const resp = await fetch(TURNSTILE_VERIFY_URL, {
      method: "POST",
      body:   form,
      // 10s — Cloudflare's siteverify is typically <100ms but we
      // don't want a hung connection to lock signup for everyone.
      signal: AbortSignal.timeout(10_000),
    });
    if (!resp.ok) {
      console.warn("[precheck] siteverify HTTP", resp.status);
      return NextResponse.json(
        { ok: false, reason: "Verification system unavailable. Try again in a moment." },
        { status: 503 },
      );
    }
    verifyJson = (await resp.json()) as TurnstileVerifyResponse;
  } catch (e) {
    console.warn("[precheck] siteverify errored:", e);
    return NextResponse.json(
      { ok: false, reason: "Verification system unavailable. Try again in a moment." },
      { status: 503 },
    );
  }

  if (!verifyJson.success) {
    // Cloudflare error codes for diagnostic logging only — never
    // surfaced to the user (we don't want bots to learn WHICH check
    // they failed and tune around it).
    console.info("[precheck] turnstile rejected:", verifyJson["error-codes"]);
    return NextResponse.json(
      { ok: false, reason: "Verification failed. Please refresh and try again." },
      { status: 400 },
    );
  }

  return NextResponse.json({ ok: true });
}
