/**
 * Sentry — EDGE runtime init (middleware, edge route handlers).
 *
 * Loaded by `instrumentation.ts` when NEXT_RUNTIME === "edge". Edge
 * runtime is V8-isolate-based and has fewer APIs than Node, but Sentry
 * supports a subset of integrations there.
 *
 * Defaults match the server config. No Session Replay (browser-only),
 * no tracing of HTTP modules (not available in edge).
 */

import * as Sentry from "@sentry/nextjs";
import { scrubEvent } from "@/lib/sentry-scrub";

const DSN = process.env.SENTRY_DSN ?? process.env.NEXT_PUBLIC_SENTRY_DSN;
const ENV = process.env.SENTRY_ENVIRONMENT ?? process.env.NODE_ENV ?? "development";
const TRACES_RATE = parseFloat(
  process.env.SENTRY_TRACES_SAMPLE_RATE ??
    (ENV === "development" ? "1.0" : "0.1"),
);

if (DSN) {
  Sentry.init({
    dsn: DSN,
    environment: ENV,
    release: process.env.SENTRY_RELEASE,
    sendDefaultPii: false,
    tracesSampleRate: TRACES_RATE,

    beforeSend(event) {
      try { return scrubEvent(event); } catch { return event; }
    },
  });
}
