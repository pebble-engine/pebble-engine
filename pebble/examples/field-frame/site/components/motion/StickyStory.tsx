"use client";
import { useRef } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/** Scroll-narrative built from repeated <StickyStep>s. Each step is a tall
 *  two-column row; the visual column pins (CSS sticky) while the prose scrolls
 *  past it, then releases to the next step. Pure CSS sticky — no scroll
 *  listeners, no active-index state — so it's robust and reduced-motion-safe.
 *
 *  Compiler-friendly: the block template repeats <StickyStep> via list markers,
 *  so StickyStorySection just renders its children. */
export function StickyStorySection({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return <section className={className}>{children}</section>;
}

/** One step. `media` pins to the viewport while `children` (the prose) scrolls.
 *  EDIT-SAFE: prose and media are plain children — each keeps its own
 *  data-pebble-id; motion only fades the prose in. `reverse` alternates which
 *  side the media sits on for visual rhythm. */
export function StickyStep({
  media,
  children,
  className,
  reverse = false,
}: {
  media: ReactNode;
  children: ReactNode;
  className?: string;
  reverse?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  return (
    <div
      ref={ref}
      className={`grid min-h-screen grid-cols-1 items-center gap-12 px-8 md:grid-cols-2 ${className ?? ""}`}
    >
      <div className={reverse ? "md:order-2" : ""}>
        <div className="sticky top-[20vh] overflow-hidden rounded-3xl">{media}</div>
      </div>
      <motion.div
        className={reverse ? "md:order-1" : ""}
        initial={reduce ? false : { opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    </div>
  );
}

export default StickyStorySection;
