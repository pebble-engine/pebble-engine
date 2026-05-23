"use client";

import { useEffect } from "react";
import * as Sentry from "@sentry/nextjs";

// Catches errors in the root layout itself (AuthProvider, fonts, etc.).
// Must be a very minimal component — cannot rely on any layout providers,
// fonts, or CSS variables since those may be what failed.
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Sentry: capture root-level errors that React's normal error
    // boundary can't reach. No-op if SENTRY_DSN isn't configured.
    Sentry.captureException(error);
    console.error("[pebble global error]", error);
  }, [error]);

  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          minHeight: "100dvh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: "system-ui, sans-serif",
          background: "#0a0a0a",
          color: "#fafaf9",
          textAlign: "center",
          padding: "2rem",
          gap: "1.5rem",
        }}
      >
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>
          Something went wrong.
        </h1>
        <p style={{ color: "#a8a29e", margin: 0, maxWidth: "28rem" }}>
          An unexpected error occurred. Your work is safe.
          {error.digest && (
            <span style={{ display: "block", fontSize: "0.75rem", fontFamily: "monospace", marginTop: "0.5rem" }}>
              ref: {error.digest}
            </span>
          )}
        </p>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            onClick={reset}
            style={{
              padding: "0.625rem 1.25rem",
              borderRadius: "999px",
              background: "#205661",
              color: "#fff",
              border: "none",
              cursor: "pointer",
              fontSize: "0.875rem",
              fontWeight: 600,
            }}
          >
            Try again
          </button>
          <a
            href="/"
            style={{
              padding: "0.625rem 1.25rem",
              borderRadius: "999px",
              background: "transparent",
              color: "#fafaf9",
              border: "1px solid #292524",
              cursor: "pointer",
              fontSize: "0.875rem",
              fontWeight: 600,
              textDecoration: "none",
            }}
          >
            Go home
          </a>
        </div>
      </body>
    </html>
  );
}
