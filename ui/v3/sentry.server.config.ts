/**
 * Sentry — Node.js SERVER runtime init.
 *
 * Loaded by `instrumentation.ts` when NEXT_RUNTIME === "nodejs" — i.e.
 * during SSR, server components, server actions, and route handlers
 * that aren't on the edge.
 *
 * Defaults match instrumentation-client.ts: PII off, conservative
 * sample rates, shared secret scrubber. Session Replay is browser-
 * only, so it's omitted here.
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
