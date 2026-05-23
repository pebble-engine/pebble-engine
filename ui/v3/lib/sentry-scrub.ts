/**
 * Sentry payload scrubber — keep in sync with `pebble_engine.py`'s
 * Python `_sentry_scrub` function. Identical pattern set so the engine
 * and v3 strip the same secrets before anything ships to Sentry.
 *
 * Walks the event object recursively, applying regex replacements to
 * every string. Safe in node, browser, AND edge runtime — uses only
 * regex + plain object traversal, no Node-only APIs.
 *
 * Defense-in-depth on top of `sendDefaultPii: false` — that gate
 * stops Sentry from auto-capturing cookies/headers/IPs, but it doesn't
 * stop a secret that ends up in an exception message or a captured
 * local variable.
 */

const SCRUBBERS: Array<[RegExp, string]> = [
  // LLM provider keys
  [/sk-ant-api\d+-[A-Za-z0-9_-]{40,}/g,                 "<ANTHROPIC_KEY>"],
  [/sk-or-v1-[A-Za-z0-9]{40,}/g,                        "<OPENROUTER_KEY>"],

  // Stripe
  [/sk_(test|live)_[A-Za-z0-9]{20,}/g,                  "<STRIPE_SK>"],
  [/rk_(test|live)_[A-Za-z0-9]{20,}/g,                  "<STRIPE_RK>"],
  [/whsec_[A-Za-z0-9]{20,}/g,                           "<WEBHOOK_SECRET>"],

  // Supabase service-role / user JWTs (3-segment base64url)
  [/eyJ[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{30,}\.[A-Za-z0-9_-]{20,}/g, "<JWT>"],

  // Email redaction — keep first char + domain for triage
  // (e.g. "marc@example.com" → "m***@example.com")
  [/\b([A-Za-z0-9_.+-])[A-Za-z0-9_.+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b/g, "$1***@$2"],
];

function scrubString(s: string): string {
  let out = s;
  for (const [pattern, replacement] of SCRUBBERS) {
    out = out.replace(pattern, replacement);
  }
  return out;
}

/** Recursively scrub strings inside a Sentry event payload. */
export function scrubEvent<T>(value: T): T {
  if (typeof value === "string") {
    return scrubString(value) as unknown as T;
  }
  if (Array.isArray(value)) {
    return value.map((v) => scrubEvent(v)) as unknown as T;
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = scrubEvent(v);
    }
    return out as unknown as T;
  }
  return value;
}
