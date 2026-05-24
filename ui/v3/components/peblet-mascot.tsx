"use client";

/**
 * Peblet — the kawaii pebble mascot Marc commissioned (2026-05-23).
 *
 * Renders /brand/peblet.png at the requested size with a graceful
 * fallback: if the asset is missing, a styled circle with "P" appears
 * so the UI never breaks on a missing-image 404.
 *
 * The mascot does double duty: large in the chat panel header, smaller
 * as a chat-bubble avatar, mid-size in the project-list empty state.
 * Single component so every appearance shares the same identity.
 */

import { useState } from "react";

export type PebletSize = "xs" | "sm" | "md" | "lg" | "xl";

const SIZE_PX: Record<PebletSize, number> = {
  xs: 28,
  sm: 40,
  md: 80,
  lg: 160,
  xl: 240,
};

export function PebletMascot({
  size = "md",
  className = "",
  animate = false,
}: {
  size?: PebletSize;
  className?: string;
  /** Adds a gentle bobbing animation — used in the chat header. */
  animate?: boolean;
}) {
  const px = SIZE_PX[size];
  const [errored, setErrored] = useState(false);

  if (errored) {
    return (
      <div
        className={`inline-flex items-center justify-center rounded-full bg-foreground text-background font-extrabold ${className}`}
        style={{ width: px, height: px, fontSize: px * 0.5 }}
        aria-label="Peblet"
      >
        P
      </div>
    );
  }

  return (
    <div
      className={`inline-block shrink-0 ${animate ? "peblet-bob" : ""} ${className}`}
      style={{ width: px, height: px }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src="/brand/peblet.png"
        alt="Peblet"
        width={px}
        height={px}
        style={{ width: px, height: px, objectFit: "contain" }}
        onError={() => setErrored(true)}
        draggable={false}
      />
      <style>{`
        @keyframes peblet-bob {
          0%, 100% { transform: translateY(0) rotate(-2deg); }
          50%      { transform: translateY(-6px) rotate(2deg); }
        }
        .peblet-bob { animation: peblet-bob 3.6s ease-in-out infinite; }
        @media (prefers-reduced-motion: reduce) {
          .peblet-bob { animation: none; }
        }
      `}</style>
    </div>
  );
}
