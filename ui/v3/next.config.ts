import type { NextConfig } from "next";

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
 * Tighten further (nonce-based, drop unsafe-*) once we know nothing
 * breaks — that's a follow-up Observatory A+ pass.
 */
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
      "style-src 'self' 'unsafe-inline'",
      "font-src 'self' data:",
      "img-src 'self' data: blob: https:",
      "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://plausible.io https://*.up.railway.app https://api.stripe.com https://accounts.google.com https://github.com https://api.github.com",
      "frame-src 'self' https://*.up.railway.app https://js.stripe.com https://hooks.stripe.com https://accounts.google.com https://github.com",
      "frame-ancestors 'self'",
      "base-uri 'self'",
      "form-action 'self' https://accounts.google.com https://github.com https://*.supabase.co",
      "object-src 'none'",
      "upgrade-insecure-requests",
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

export default nextConfig;
