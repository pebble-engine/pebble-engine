import type { NextConfig } from "next";

/**
 * Proxy /api/* and /preview/* to the Python engine (localhost:8000) during
 * dev. Production deployment will need a different strategy (e.g. Vercel
 * rewrites or putting the engine behind Next.js' edge runtime).
 */
const PEBBLE_ENGINE_URL = process.env.PEBBLE_ENGINE_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/api/:path*",     destination: `${PEBBLE_ENGINE_URL}/api/:path*` },
      { source: "/preview/:path*", destination: `${PEBBLE_ENGINE_URL}/preview/:path*` },
    ];
  },
};

export default nextConfig;
