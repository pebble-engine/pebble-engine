/**
 * Next.js 16 instrumentation hook — dispatches Sentry init to the
 * right runtime config based on where the code is running.
 *
 * The browser runtime is auto-loaded by Next.js from
 * `instrumentation-client.ts` (no `register()` call needed there).
 * This file handles server + edge runtimes.
 *
 * `onRequestError` lets Sentry capture exceptions in server actions /
 * route handlers / RSC renders that React's error boundaries can't.
 */

import * as Sentry from "@sentry/nextjs";

export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    await import("./sentry.server.config");
  }
  if (process.env.NEXT_RUNTIME === "edge") {
    await import("./sentry.edge.config");
  }
}

export const onRequestError = Sentry.captureRequestError;
