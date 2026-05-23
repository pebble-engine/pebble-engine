/**
 * Sentry — BROWSER runtime init.
 *
 * Auto-loaded by Next.js 16+ at app boot. Runs ONCE per page load in
 * the user's browser. Captures unhandled JS errors, unhandled promise
 * rejections, React render errors (via the App-Router error boundary
 * + global-error.tsx), and Session Replay.
 *
 * Defaults tuned for the free Developer tier (5K errors, 5M spans,
 * 50 replays / month) and Pebble's PII posture (matches engine):
 *   - sendDefaultPii: false      — never auto-capture cookies / headers / IP
 *   - tracesSampleRate           — 1.0 in dev, 0.1 in prod (override via env)
 *   - replaysSessionSampleRate   — 0.1 (10% of sessions get a replay baseline)
 *   - replaysOnErrorSampleRate   — 1.0 (always replay sessions that errored)
 *
 * beforeSend scrubs known secret patterns + emails before anything
 * leaves the browser (defense-in-depth on top of sendDefaultPii).
 */

import * as Sentry from "@sentry/nextjs";
import { scrubEvent } from "@/lib/sentry-scrub";

const DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;
const ENV = process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ?? process.env.NODE_ENV ?? "development";
const TRACES_RATE = parseFloat(
  process.env.NEXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE ??
    (ENV === "development" ? "1.0" : "0.1"),
);

if (DSN) {
  Sentry.init({
    dsn: DSN,
    environment: ENV,
    release: process.env.NEXT_PUBLIC_SENTRY_RELEASE,
    sendDefaultPii: false,

    tracesSampleRate: TRACES_RATE,

    // Session Replay — record session at 10% baseline, 100% on any error.
    // Replays count separately from errors against the quota.
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,

    integrations: [Sentry.replayIntegration()],

    beforeSend(event) {
      try { return scrubEvent(event); } catch { return event; }
    },
  });
}

// Required hook for Next.js's app-router navigation instrumentation.
// Without this, Sentry can't track route changes as spans.
export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
