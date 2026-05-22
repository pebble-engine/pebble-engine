import type { NextConfig } from "next";

/**
 * Proxy /api/* and /preview/* to the Python engine (localhost:8000) during
 * dev. Production deployment will need a different strategy (e.g. Vercel
 * rewrites or putting the engine behind Next.js' edge runtime).
 */
const PEBBLE_ENGINE_URL = process.env.PEBBLE_ENGINE_URL ?? "http://127.0.0.1:8000";

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
};

export default nextConfig;
