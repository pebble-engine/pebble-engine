"use client";

/**
 * TakeoffMoment — Phase 43.7 (2026-05-21).
 *
 * Rewrite. Marc didn't love the literal Pebble-logo rocket SVG (Phase
 * 43.5). The new direction: keep the "Ready for takeoff?" copy and the
 * scroll-down cue into pricing, but replace the rocket/starfield with
 * a scroll-driven SUNRISE GRADIENT that visibly shifts color as the
 * section traverses the viewport.
 *
 * Three stacked gradient layers crossfade via opacity values bound to
 * scrollYProgress:
 *
 *   layer 1 (PRE-DAWN):     deep indigo → midnight purple
 *   layer 2 (DAWN BREAKING): rich purple → coral → warm peach
 *   layer 3 (FULL SUNRISE):  warm peach → soft pink → cream
 *
 * As the user scrolls down through the section, the visual reads as
 * actually rising into morning light — the "takeoff" metaphor without
 * the cartoon rocket. Top of section: pre-dawn dark. Middle: dawn
 * breaking. Bottom: full daylight blending into the cream of the page
 * below.
 *
 * Reduced-motion: pin to layer 2 (mid-dawn) statically so the visual
 * still reads but no animation fires.
 */

import React from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
} from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const EASE = [0.22, 1, 0.36, 1] as const;

export interface TakeoffMomentProps {
  /** Scroll target for the chevron CTA. Defaults to the pricing anchor. */
  scrollTo?: string;
  className?: string;
}

export function TakeoffMoment({ scrollTo = "#pricing", className = "" }: TakeoffMomentProps) {
  const prefersReduced = useReducedMotion() ?? false;
  const containerRef   = React.useRef<HTMLDivElement>(null);

  // Track the section's position relative to the viewport.
  // scrollYProgress goes 0 (section's top hits viewport BOTTOM) → 1
  // (section's bottom hits viewport TOP). For a sticky-pinned section
  // that's slightly weird because the pinned inner stays put while
  // the outer wrapper scrolls; the math still produces a smooth 0→1
  // sweep across the user's scroll, which is what we want.
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  // Three layers, opacity blended via crossfade as scroll progresses.
  // Pre-dawn dominates at the top, dawn breaks in the middle, full
  // sunrise lands at the bottom — and the section transitions smoothly
  // into the cream of the pricing section below.
  const preDawnOpacity = useTransform(scrollYProgress, [0,    0.35, 0.6 ], [1, 1, 0]);
  const dawnOpacity    = useTransform(scrollYProgress, [0.15, 0.5,  0.85], [0, 1, 0]);
  const sunriseOpacity = useTransform(scrollYProgress, [0.45, 0.75, 1   ], [0, 1, 1]);

  // Headline brightness — text starts off WHITE (against dark pre-dawn)
  // and shifts to FOREGROUND charcoal (against the cream sunrise) as
  // the scroll progresses. Drives the headline + subtitle color.
  // Driven via a single CSS variable on the wrapper so both elements
  // inherit it.
  const textColor = useTransform(
    scrollYProgress,
    [0, 0.55, 0.85],
    ["#ffffff", "#ffffff", "#1f1d1a"],
  );

  // Chevron darkens too — same curve.
  const chevronColor = useTransform(
    scrollYProgress,
    [0, 0.6, 1],
    ["rgba(255,255,255,0.75)", "rgba(255,255,255,0.8)", "rgba(31,29,26,0.6)"],
  );

  const handleScroll = () => {
    if (!scrollTo) return;
    const target = document.querySelector(scrollTo) as HTMLElement | null;
    target?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <div
      ref={containerRef}
      className={cn("relative w-full h-full overflow-hidden", className)}
    >
      {/* Layer 1 — pre-dawn. Deep indigo top → midnight purple bottom. */}
      <motion.div
        aria-hidden
        style={prefersReduced ? { opacity: 0.6 } : { opacity: preDawnOpacity }}
        className="absolute inset-0"
      >
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(180deg, #0a0e2a 0%, #1d1740 45%, #2a1f4a 100%)",
          }}
        />
      </motion.div>

      {/* Layer 2 — dawn breaking. Rich purple → coral → warm peach. */}
      <motion.div
        aria-hidden
        style={prefersReduced ? { opacity: 1 } : { opacity: dawnOpacity }}
        className="absolute inset-0"
      >
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(180deg, #3a2055 0%, #7a3a6f 40%, #d96d52 80%, #e88b5c 100%)",
          }}
        />
      </motion.div>

      {/* Layer 3 — full sunrise. Warm peach → soft pink → cream.
          Blends seamlessly into the page background (color-sand) at
          the bottom so the section transitions into pricing. */}
      <motion.div
        aria-hidden
        style={prefersReduced ? { opacity: 0 } : { opacity: sunriseOpacity }}
        className="absolute inset-0"
      >
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(180deg, #e88b5c 0%, #f4b88a 40%, #f5d5b8 75%, #f7f3ec 100%)",
          }}
        />
      </motion.div>

      {/* Foreground copy — scroll-tied color so it stays legible against
          whichever gradient layer is dominant. */}
      <motion.div
        className="absolute inset-0 flex flex-col items-center justify-center text-center px-4 max-w-2xl mx-auto pointer-events-none"
        style={prefersReduced ? { color: "#ffffff" } : { color: textColor }}
      >
        <motion.h2
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.8, ease: EASE }}
          className="font-[family-name:var(--font-cormorant)] italic text-4xl sm:text-6xl lg:text-7xl drop-shadow-[0_4px_24px_rgba(0,0,0,0.25)]"
        >
          Ready for takeoff?
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.7, ease: EASE, delay: 0.2 }}
          className="mt-4 text-base sm:text-lg opacity-90"
        >
          Pick a plan. We&apos;ll handle the rest.
        </motion.p>
      </motion.div>

      {/* Scroll-down cue. Bottom-centered, pulses to invite scroll. */}
      <motion.button
        type="button"
        onClick={handleScroll}
        aria-label="Scroll to pricing"
        style={prefersReduced ? { color: "rgba(31,29,26,0.6)" } : { color: chevronColor }}
        className={cn(
          "absolute left-1/2 -translate-x-1/2 bottom-6 sm:bottom-10",
          "inline-flex flex-col items-center gap-1",
          "text-[10px] uppercase tracking-[0.18em] font-semibold",
          "hover:opacity-100 transition-opacity duration-200",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent rounded-md px-2 py-1",
        )}
      >
        <span>Pricing below</span>
        <motion.span
          animate={prefersReduced ? {} : { y: [0, 4, 0] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
        >
          <ChevronDown className="w-5 h-5" aria-hidden />
        </motion.span>
      </motion.button>
    </div>
  );
}

export default TakeoffMoment;
