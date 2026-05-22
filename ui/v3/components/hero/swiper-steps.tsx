"use client";

/**
 * SwiperSteps — Phase 40f (2026-05-21).
 *
 * Horizontal swiper for the §2 "From sentence to site." value prop.
 * Replaces the StickyScrollStack — Marc's call: pinned-stack on §2 was
 * overkill + ate too much vertical real estate. A standard auto-advancing
 * card swiper communicates the 3 steps without hijacking the whole page.
 *
 * Behavior:
 *   - 3 cards laid out horizontally inside a viewport
 *   - Auto-advances every 5s
 *   - Click any dot to jump to that step (pauses auto-advance for the
 *     rest of the session)
 *   - Dots show fill-progress while auto-advance is running
 *   - On the dots: hover/focus styling for keyboard nav
 *   - Smooth slide transition + crossfade (350ms cinematic ease)
 */

import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { type } from "@/lib/type";

export type SwiperStep = {
  id:      string;
  icon?:   ReactNode;
  eyebrow?: string;
  title:   string;
  body:    string;
};

type Props = {
  steps:    SwiperStep[];
  /** Section anchor id. */
  id?:      string;
  /** Heading shown above the swiper. */
  heading?: string;
  /** Subhead shown below the heading. */
  subhead?: string;
  /** Auto-advance interval in ms. Default 5000. Set 0 to disable. */
  intervalMs?: number;
  className?: string;
};

const EASE = [0.22, 1, 0.36, 1] as const;

export function SwiperSteps({
  steps,
  id,
  heading,
  subhead,
  intervalMs = 5000,
  className = "",
}: Props) {
  const [idx, setIdx]                = useState(0);
  const [autoplaying, setAutoplaying] = useState(intervalMs > 0);
  const [progress, setProgress]       = useState(0);
  const tickRef = useRef<number | null>(null);

  // Auto-advance with progress tracking
  useEffect(() => {
    if (!autoplaying || intervalMs <= 0) return;
    let startedAt = performance.now();
    let raf = 0;
    const loop = (now: number) => {
      const elapsed = now - startedAt;
      const pct = Math.min(1, elapsed / intervalMs);
      setProgress(pct);
      if (pct >= 1) {
        setIdx((i) => (i + 1) % steps.length);
        startedAt = now;
        setProgress(0);
      }
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    tickRef.current = raf;
    return () => cancelAnimationFrame(raf);
  }, [autoplaying, intervalMs, steps.length, idx]);

  const goTo = (next: number) => {
    setAutoplaying(false);
    setProgress(0);
    setIdx(((next % steps.length) + steps.length) % steps.length);
  };

  const step = steps[idx];

  return (
    <section id={id} className={`relative px-4 max-w-5xl mx-auto py-24 ${className}`}>
      {/* Heading + subhead — cinematic whileInView entrance */}
      {heading && (
        <motion.div
          initial={{ opacity: 0, y: 48, scale: 0.92 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.9, ease: EASE }}
          className="text-center mb-12 space-y-4"
        >
          <h2 className={`${type.display.l} text-foreground`}>{heading}</h2>
          {subhead && (
            <p className="text-lg max-w-xl mx-auto text-muted-foreground">
              {subhead}
            </p>
          )}
        </motion.div>
      )}

      {/* Swiper viewport */}
      <div className="relative">
        <div className="overflow-hidden rounded-3xl border border-border bg-card shadow-[0_24px_80px_rgba(31,29,26,0.08)]">
          <div className="relative h-[420px] sm:h-[360px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: 60 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -60 }}
                transition={{ duration: 0.45, ease: EASE }}
                className="absolute inset-0 flex flex-col justify-center px-10 py-10"
              >
                {step.eyebrow && (
                  <p className={`${type.eyebrow} mb-3`}>{step.eyebrow}</p>
                )}
                {step.icon && (
                  <div className="mb-6 text-[#3054ff]">{step.icon}</div>
                )}
                <h3 className={`${type.heading.l} mb-4 text-foreground max-w-md`}>
                  {step.title}
                </h3>
                <p className="text-muted-foreground leading-relaxed text-base max-w-xl">
                  {step.body}
                </p>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Dots — visual progress + click-to-jump */}
        <div className="flex items-center justify-center gap-2 mt-6">
          {steps.map((s, i) => (
            <button
              key={s.id}
              type="button"
              onClick={() => goTo(i)}
              className="group p-2 -m-2 focus-visible:outline-none"
              aria-label={`Go to step ${i + 1}: ${s.title}`}
            >
              <span
                className={`block h-1 rounded-full transition-all duration-300 ${
                  i === idx
                    ? "w-12 bg-foreground/15"
                    : "w-6 bg-foreground/15 group-hover:bg-foreground/30"
                }`}
              >
                {/* Active fill */}
                {i === idx && (
                  <span
                    className="block h-full rounded-full bg-foreground transition-all duration-100"
                    style={{ width: autoplaying ? `${progress * 100}%` : "100%" }}
                  />
                )}
              </span>
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
