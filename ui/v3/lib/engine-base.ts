// Single source of truth for the engine origin used by direct (CORS) calls
// and engine-served iframe srcs.
//
// Normalizes a host-only NEXT_PUBLIC_PEBBLE_ENGINE_URL to an ABSOLUTE https://
// origin. If the env var is set without a scheme (e.g.
// "web-production-xxxx.up.railway.app"), a naive concat yields a scheme-less
// string the browser resolves RELATIVE to the app origin — so `/api/x` becomes
// `https://<app>/<engine-host>/api/x` and every call 404s against the frontend.
// (Prod incident 2026-06-08: Vercel had the var set without the scheme.)
//
// Every module that talks to the engine MUST import ENGINE_BASE from here
// rather than re-reading process.env inline, so the normalization can't drift.
export function normalizeEngineBase(raw: string): string {
  const trimmed = (raw || "").trim().replace(/\/+$/, "");
  if (!trimmed) return "";
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}

export const ENGINE_BASE: string = normalizeEngineBase(
  process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "",
);
