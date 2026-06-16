"use client";

/**
 * TurnstileWidget — Cloudflare Turnstile invisible CAPTCHA.
 *
 * Marc 2026-05-24 security review: defeats per-IP rate-limit bypass
 * via rotating proxies. The token returned by the widget is verified
 * server-side by /api/auth/precheck before Supabase signup proceeds.
 *
 * Usage:
 *
 *   const [token, setToken] = useState<string | null>(null);
 *   <TurnstileWidget onToken={setToken} />
 *   // Pass `token` to /api/auth/precheck along with the email.
 *
 * Loads the Cloudflare script once per page lifetime via a global
 * sentinel — multiple widget instances on the same page (signup +
 * login both rendered) share the loaded SDK.
 *
 * Gracefully no-ops when NEXT_PUBLIC_TURNSTILE_SITE_KEY isn't set —
 * onToken("DEV_BYPASS") fires immediately so dev environments
 * without Cloudflare config don't break the signup form. The server-
 * side precheck route mirrors this dev-fallback.
 */

import { useEffect, useRef } from "react";

const SCRIPT_SRC = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
const SCRIPT_ID = "cf-turnstile-sdk";

type TurnstileGlobal = {
  render: (
    element: HTMLElement,
    options: {
      sitekey: string;
      callback: (token: string) => void;
      "error-callback"?: () => void;
      "expired-callback"?: () => void;
      theme?: "light" | "dark" | "auto";
      size?: "normal" | "compact" | "invisible" | "flexible";
    },
  ) => string;
  reset: (widgetId?: string) => void;
};

declare global {
  interface Window {
    turnstile?: TurnstileGlobal;
  }
}

function loadScriptOnce(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (typeof document === "undefined") { reject(new Error("no document")); return; }
    if (window.turnstile) { resolve(); return; }
    const existing = document.getElementById(SCRIPT_ID) as HTMLScriptElement | null;
    if (existing) {
      // Already in flight — wait for it.
      existing.addEventListener("load", () => resolve(), { once: true });
      existing.addEventListener("error", () => reject(new Error("script error")), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.id = SCRIPT_ID;
    script.src = SCRIPT_SRC;
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("script load failed"));
    document.head.appendChild(script);
  });
}

export type TurnstileWidgetProps = {
  /** Called with the verification token when the user passes the
   *  challenge. Fires with "DEV_BYPASS" when the site key isn't
   *  configured (local dev). Called again on re-render if the user
   *  resets or the token expires. */
  onToken: (token: string) => void;
  /** Called when the challenge errors out. Optional. */
  onError?: () => void;
  /** Visual theme. Defaults to "auto" (matches OS preference). */
  theme?: "light" | "dark" | "auto";
};

export function TurnstileWidget({ onToken, onError, theme = "auto" }: TurnstileWidgetProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const widgetIdRef = useRef<string | null>(null);

  useEffect(() => {
    const siteKey = (process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY || "").trim();
    const isLocalHost =
      typeof window !== "undefined"
      && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1");
    // Production Turnstile keys are hostname-bound (pebbleapp.ai). On
    // localhost the widget fails silently and signup stays disabled.
    if (!siteKey || isLocalHost) {
      onToken("DEV_BYPASS");
      return;
    }
    let cancelled = false;
    loadScriptOnce()
      .then(() => {
        if (cancelled) return;
        const ts = window.turnstile;
        const el = containerRef.current;
        if (!ts || !el) return;
        widgetIdRef.current = ts.render(el, {
          sitekey: siteKey,
          theme,
          size: "flexible",
          callback: (token: string) => onToken(token),
          "error-callback": () => onError?.(),
          // On expiry, clear the previous token so the form can't be
          // submitted with stale verification. Parent re-renders the
          // widget to issue a fresh challenge if needed.
          "expired-callback": () => onToken(""),
        });
      })
      .catch(() => {
        // Script failed to load — let the form proceed without
        // Turnstile rather than block the user. The server-side
        // precheck will reject the unverified token, so this is
        // best-effort fail-OPEN at the widget layer + fail-CLOSED
        // at the route layer.
        console.warn("[turnstile] failed to load — server will reject");
        onError?.();
      });
    return () => {
      cancelled = true;
      // Best-effort reset so a re-mount doesn't leave a stale
      // widget rendered above the form.
      try {
        if (widgetIdRef.current && window.turnstile?.reset) {
          window.turnstile.reset(widgetIdRef.current);
        }
      } catch {
        // Cleanup throwing isn't fatal; the page is going away.
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // mount-once; re-rendering would create duplicate widgets

  return <div ref={containerRef} className="my-3 min-h-[65px]" />;
}
