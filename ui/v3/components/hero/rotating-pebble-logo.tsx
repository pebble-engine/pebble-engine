"use client";

/**
 * RotatingPebbleLogo — extracted from welcome-phase.tsx on 2026-05-22.
 *
 * The brand wordmark that cycles through "Pebble" in 8 languages with
 * a shimmering gradient clip. Originally lived inside welcome-phase
 * as a private component; promoted to its own module so the new Trust
 * Charter seal (Phase 52) can use it as the centerpiece. Welcome-phase
 * keeps importing from here so it stays the single source of truth.
 */

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";

/** "Pebble" translated into 8 world languages — for the rotating wordmark. */
export const PEBBLE_LANGS = [
  "Pebble",     // English
  "Guijarro",   // Español
  "Caillou",    // Français
  "Kiesel",     // Deutsch
  "Seixo",      // Português
  "小石",        // 日本語
  "자갈",        // 한국어
  "Ciottolo",   // Italiano
] as const;

/**
 * Foreground-aware shimmer for light / dark surfaces (footer, etc.).
 * Uses CSS custom properties so it resolves to the right tones in each
 * theme — near-black on sand in light mode, near-white on #0a0a0a in dark.
 */
export const shimmerForegroundStyle: React.CSSProperties = {
  backgroundImage:
    "linear-gradient(90deg, var(--color-muted-foreground) 0%, var(--color-foreground) 40%, var(--color-foreground) 60%, var(--color-muted-foreground) 100%)",
  backgroundSize: "200% auto",
};

/**
 * Cycles through PEBBLE_LANGS with a shimmering gradient clipped to the
 * text. Usable on both dark (nav) and light (footer, trust seal)
 * surfaces — just pass the appropriate shimmerStyle.
 */
export function RotatingPebbleLogo({
  shimmerStyle,
  className = "",
}: {
  shimmerStyle: React.CSSProperties;
  className?: string;
}) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % PEBBLE_LANGS.length), 2800);
    return () => clearInterval(id);
  }, []);

  return (
    <MotionConfig reducedMotion="never">
      {/* aria-label="Pebble" so screen readers always hear the brand name */}
      <span aria-label="Pebble" className={`relative inline-block font-logo tracking-[0.12em] ${className}`}>
        {/* invisible max-width anchor — "Guijarro" is the longest word */}
        <span aria-hidden className="invisible select-none">Guijarro</span>
        <AnimatePresence mode="wait">
          <motion.span
            key={PEBBLE_LANGS[idx]}
            initial={{ opacity: 0, y: 6 }}
            animate={{
              opacity: 1,
              y: 0,
              backgroundPosition: ["0% 0%", "200% 0%"],
            }}
            exit={{ opacity: 0, y: -6 }}
            transition={{
              opacity: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
              y:       { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
              backgroundPosition: { duration: 3.5, repeat: Infinity, ease: "linear" },
            }}
            className="absolute left-0 top-0 bg-clip-text text-transparent whitespace-nowrap"
            style={shimmerStyle}
          >
            {PEBBLE_LANGS[idx]}
          </motion.span>
        </AnimatePresence>
      </span>
    </MotionConfig>
  );
}
