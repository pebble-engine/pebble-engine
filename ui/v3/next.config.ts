import type { NextConfig } from "next";
import { withSentryConfig } from "@sentry/nextjs";

/**
 * Proxy /api/* and /preview/* to the Python engine (localhost:8000) during
 * dev. Production deployment will need a different strategy (e.g. Vercel
 * rewrites or putting the engine behind Next.js' edge runtime).
 */
const PEBBLE_ENGINE_URL = process.env.PEBBLE_ENGINE_URL ?? "http://127.0.0.1:8000";

/**
 * Phase 55 (2026-05-22) — security headers for Mozilla Observatory.
 * Initial scan of pebble-engine-oovy.vercel.app came back C (50/100):
 * HSTS was the only passing security-header test. Adding CSP +
 * X-Frame-Options + X-Content-Type-Options + Referrer-Policy +
 * Permissions-Policy targets A.
 *
 * CSP is conservative — keeps 'unsafe-inline' for Next.js's inline
 * scripts/styles + 'unsafe-eval' for chunk-loading. Locks down
 * connect/frame to known origins:
 *   - Supabase (https + wss for realtime auth)
 *   - Pebble engine on Railway
 *   - Plausible analytics
 *   - Stripe.js for checkout sessions
 *   - Self everywhere else
 *
 * Dev vs prod split (Phase 56a):
 *   - Dev adds http://localhost:8000 + http://127.0.0.1:8000 to connect-src
 *     because NEXT_PUBLIC_PEBBLE_ENGINE_URL bypasses the Next.js proxy so
 *     long SSE streams (generate-stream) don't get killed by the dev proxy.
 *   - Dev omits upgrade-insecure-requests so HTTP localhost calls aren't
 *     silently upgraded to HTTPS (which also fails locally).
 */
const isDev = process.env.NODE_ENV === "development";

// Extra connect-src hosts when running locally so the direct-to-engine
// calls allowed by NEXT_PUBLIC_PEBBLE_ENGINE_URL aren't CSP-blocked.
const devConnectSrc = isDev
  ? " http://localhost:8000 http://127.0.0.1:8000 ws://localhost:* ws://127.0.0.1:*"
  : "";

// Extra frame-src hosts when running locally so the template-gallery
// iframe renders. v3 is on :3001 and several iframe sources exist:
//   - Engine static-export previews:   http://localhost:8000/preview-template/...
//   - Per-template legacy dev servers: http://127.0.0.1:3060-3199 range
//     (service_pro, luxe_beauty, ink_studio, etc. spin up on those ports)
// CSP port-wildcards (http://localhost:*) cover both without enumerating.
// In prod, *.up.railway.app + customer subdomains are already covered
// by the base frame-src list below.
const devFrameSrc = isDev
  ? " http://localhost:* http://127.0.0.1:*"
  : "";

const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options",        value: "SAMEORIGIN" },
  { key: "Referrer-Policy",        value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy",     value: "camera=(), microphone=(self), geolocation=(), interest-cohort=(), payment=(self)" },
  {
    key: "Content-Security-Policy",
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://plausible.io https://*.vercel-scripts.com https://js.stripe.com",
      // Sentry Replay (and any other monitoring SDK that spawns workers
      // from blob URLs) needs worker-src. Without an explicit directive,
      // browsers fall back to script-src — which is hostname-restricted
      // and rejects blob:. List blob: + self explicitly to allow internal
      // worker creation without widening the broader script-src.
      "worker-src 'self' blob:",
      "style-src 'self' 'unsafe-inline'",
      "font-src 'self' data:",
      "img-src 'self' data: blob: https:",
      `connect-src 'self' https://*.supabase.co wss://*.supabase.co https://plausible.io https://*.up.railway.app https://api.stripe.com https://accounts.google.com https://github.com https://api.github.com${devConnectSrc}`,
      `frame-src 'self' https://*.up.railway.app https://js.stripe.com https://hooks.stripe.com https://accounts.google.com https://github.com https://maps.google.com${devFrameSrc}`,
      "frame-ancestors 'self'",
      "base-uri 'self'",
      "form-action 'self' https://accounts.google.com https://github.com https://*.supabase.co",
      "object-src 'none'",
      // upgrade-insecure-requests is intentionally OMITTED in dev:
      // it would rewrite http://localhost:8000 → https://localhost:8000
      // which fails and defeats the direct-engine bypass.
      ...(!isDev ? ["upgrade-insecure-requests"] : []),
    ].join("; "),
  },
];

const nextConfig: NextConfig = {
  // Phase 41 (2026-05-21) — Marc couldn't reach the dev server from his
  // iPhone on the same WiFi. Next 15+ blocks cross-origin dev requests
  // (HMR / RSC payload / etc.) by default, so the page either fails to
  // load or renders broken when hit from a LAN IP. allowedDevOrigins
  // permits the named hosts. PEBBLE_DEV_ALLOWED_ORIGINS env var (comma-
  // separated) lets users add their own LAN IP without editing this file.
  allowedDevOrigins: [
    "192.168.1.238",
    "localhost",
    "127.0.0.1",
    ...(process.env.PEBBLE_DEV_ALLOWED_ORIGINS?.split(",").map((s) => s.trim()).filter(Boolean) ?? []),
  ],
  async rewrites() {
    return [
      { source: "/api/:path*",     destination: `${PEBBLE_ENGINE_URL}/api/:path*` },
      { source: "/preview/:path*", destination: `${PEBBLE_ENGINE_URL}/preview/:path*` },
    ];
  },
  async headers() {
    return [
      {
        // Apply security headers to every route — simple and uniform.
        source: "/(.*)",
        headers: SECURITY_HEADERS,
      },
    ];
  },
};

/**
 * Sentry wrapper — adds source-map upload at build time + the
 * /monitoring tunnel route at runtime.
 *
 * tunnelRoute is the important one: it makes the browser SDK POST
 * events to /monitoring (same-origin) instead of *.ingest.sentry.io.
 * That sidesteps two problems at once:
 *   1. Our CSP only lists 'self' + a small allowlist in connect-src;
 *      ingest.sentry.io is NOT on it, so without the tunnel the
 *      browser would block every Sentry POST.
 *   2. Some ad-blockers block requests to *.sentry.io.
 *
 * org / project are required for source-map upload. authToken is read
 * from SENTRY_AUTH_TOKEN env var (Sentry CLI default); leave it unset
 * locally and the wrapper silently skips upload — runtime still works.
 */
export default withSentryConfig(nextConfig, {
  org:                   "pebble-6q",
  project:               "pebble-v3",
  silent:                !process.env.CI,
  tunnelRoute:           "/monitoring",
  widenClientFileUpload: true,
  disableLogger:         true,
});
