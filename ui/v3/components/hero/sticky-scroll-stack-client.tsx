"use client";

/**
 * StickyScrollStackClient — the actual motion-driven component.
 *
 * Imported via dynamic({ ssr: false }) so useScroll never fires during
 * SSR/hydration. Eliminates the "Target ref is defined but not hydrated"
 * race that broke Phase 40e. See sticky-scroll-stack.tsx for the
 * loader wrapper + fallback shape.
 *
 * Mechanics identical to the design in the loader's docstring — only
 * difference is this module never executes during SSR.
 */

import { useRef, type ReactNode } from "react";
import { motion, useScroll, useTransform, type MotionValue } from "framer-motion";
import { type } from "@/lib/type";
import { ChevronDown } from "lucide-react";

export type StackCard = {
  id:    string;
  icon?: ReactNode;
  eyebrow?: string;
  title: string;
  body:  string;
  accent?: string;
};

type Props = {
  cards:    StackCard[];
  id?:      string;
  heading?: string;
  subhead?: string;
  closer?:  ReactNode;
  className?: string;
};

/**
 * Phase 40e.3 fix (2026-05-21) — card window math now respects the
 * pinned-vs-unpinned split.
 *
 * The OUTER section is `totalVh` tall (e.g. 360vh for 3 cards). The
 * sticky INNER is `h-screen` (100vh). Sticky positioning pins the inner
 * only while the outer container has room below the sticky child — i.e.
 * for the first `(totalVh - 100)` viewport-heights of scroll. After
 * that, the sticky bottoms out and scrolls normally with the page.
 *
 * Marc saw Card 3 never appearing because the old math distributed cards
 * across the FULL [0, 1] scrollYProgress range — so Card 3's window
 * started at 0.71 and the closer at 0.88, but sticky already unpinned
 * at 0.72 (260/360) on a 3-card stack. Cards/closer beyond the pin
 * fired off-screen.
 *
 * Fix: compress all card + heading + closer windows into the pinned
 * portion [0, pinnedRatio]. Everything from the user's perspective now
 * happens WHILE pinned. After pinnedRatio, the section unpins cleanly.
 */
function cardWindow(
  index:        number,
  total:        number,
  pinnedRatio:  number,
): {
  fadeIn:   [number, number];
  fadeOut:  [number, number];
  scaleIn:  [number, number];
  scaleOut: [number, number];
  yIn:      [number, number];
} {
  // Within the pinned portion: 12% heading reserve, 12% closer reserve,
  // rest split across cards.
  const HEADING_RESERVE = 0.12 * pinnedRatio;
  const CLOSER_RESERVE  = 0.12 * pinnedRatio;
  const pinnedUsable    = pinnedRatio - HEADING_RESERVE - CLOSER_RESERVE;
  const cardSpan        = pinnedUsable / total;
  const start           = HEADING_RESERVE + index * cardSpan;
  const fadeInEnd       = start + cardSpan * 0.55;
  const fadeOutStart    = start + cardSpan * 0.85;
  const fadeOutEnd      = start + cardSpan * 1.0;
  return {
    fadeIn:   [start, fadeInEnd],
    fadeOut:  [fadeOutStart, fadeOutEnd],
    scaleIn:  [start, fadeInEnd],
    scaleOut: [fadeOutStart, fadeOutEnd],
    yIn:      [start, fadeInEnd],
  };
}

function StackedCard({
  card,
  index,
  total,
  pinnedRatio,
  scrollYProgress,
}: {
  card:            StackCard;
  index:           number;
  total:           number;
  pinnedRatio:     number;
  scrollYProgress: MotionValue<number>;
}) {
  const w = cardWindow(index, total, pinnedRatio);
  const isLast = index === total - 1;

  const opacity = useTransform(
    scrollYProgress,
    isLast
      ? [w.fadeIn[0], w.fadeIn[1]]
      : [w.fadeIn[0], w.fadeIn[1], w.fadeOut[0], w.fadeOut[1]],
    isLast ? [0, 1] : [0, 1, 1, 0.55],
  );

  const scale = useTransform(
    scrollYProgress,
    isLast
      ? [w.scaleIn[0], w.scaleIn[1]]
      : [w.scaleIn[0], w.scaleIn[1], w.scaleOut[0], w.scaleOut[1]],
    isLast ? [0.92, 1] : [0.92, 1, 1, 0.94],
  );

  const y = useTransform(
    scrollYProgress,
    isLast
      ? [w.yIn[0], w.yIn[1]]
      : [w.yIn[0], w.yIn[1], w.fadeOut[0], w.fadeOut[1]],
    isLast ? [80, 0] : [80, 0, 0, -16],
  );

  return (
    <motion.div
      style={{ opacity, scale, y, zIndex: index + 1 }}
      className="absolute inset-0 flex items-center justify-center will-change-transform"
    >
      <div className="w-full max-w-xl p-10 rounded-3xl bg-card border border-border shadow-[0_24px_80px_rgba(31,29,26,0.12)]">
        {card.eyebrow && (
          <p className={`${type.eyebrow} mb-3`}>{card.eyebrow}</p>
        )}
        {card.icon && (
          <div className="mb-6 text-[#3054ff]">
            {card.icon}
          </div>
        )}
        <h3 className={`${type.heading.l} mb-4 text-foreground`}>{card.title}</h3>
        <p className="text-muted-foreground leading-relaxed text-base">{card.body}</p>
        {card.accent && (
          <p className="mt-5 pt-5 border-t border-border text-sm text-foreground/80">
            {card.accent}
          </p>
        )}
      </div>
    </motion.div>
  );
}

function CardDot({
  index,
  total,
  pinnedRatio,
  scrollYProgress,
}: {
  index:           number;
  total:           number;
  pinnedRatio:     number;
  scrollYProgress: MotionValue<number>;
}) {
  const w = cardWindow(index, total, pinnedRatio);
  const opacity = useTransform(scrollYProgress, [w.fadeIn[0], w.fadeIn[1]], [0.15, 1]);
  return (
    <motion.span
      style={{ opacity }}
      className="block w-1.5 h-1.5 rounded-full bg-foreground"
    />
  );
}

export default function StickyScrollStackClient({
  cards,
  id,
  heading,
  subhead,
  closer,
  className = "",
}: Props) {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });

  // Phase 40e.3 — section is `totalVh` tall; sticky inner is 100vh.
  // The sticky child is PINNED for the first (totalVh - 100) of scroll,
  // then unpins. All scroll-driven animations need to fit in that
  // pinned window OR they fire off-screen after unpin.
  const totalVh     = cards.length * 100 + 60;
  const pinnedRatio = (totalVh - 100) / totalVh;

  // Heading lands in the first 8% of the pinned window.
  const headingEnd = 0.08 * pinnedRatio;
  const headingOpacity = useTransform(scrollYProgress, [0, headingEnd], [0, 1]);
  const headingY       = useTransform(scrollYProgress, [0, headingEnd], [48, 0]);
  const headingScale   = useTransform(scrollYProgress, [0, headingEnd], [0.88, 1]);

  // Closer fires in the last 10% of the pinned window — AFTER the final
  // card has landed, BEFORE sticky unpins.
  const closerStart = 0.88 * pinnedRatio;
  const closerEnd   = 0.98 * pinnedRatio;
  const closerOpacity  = useTransform(scrollYProgress, [closerStart, closerEnd], [0, 1]);
  const closerY        = useTransform(scrollYProgress, [closerStart, closerEnd], [24, 0]);

  return (
    <section
      ref={ref}
      id={id}
      className={`relative ${className}`}
      style={{ height: `${totalVh}vh` }}
    >
      <div className="sticky top-0 h-screen flex flex-col items-center justify-center px-4 max-w-6xl mx-auto overflow-hidden">
        {heading && (
          <motion.div
            style={{ opacity: headingOpacity, y: headingY, scale: headingScale }}
            className="text-center mb-12 space-y-4 will-change-transform"
          >
            <h2 className={`${type.display.l} text-foreground`}>{heading}</h2>
            {subhead && (
              <p className="text-lg max-w-xl mx-auto text-muted-foreground">
                {subhead}
              </p>
            )}
          </motion.div>
        )}

        <div className="relative w-full max-w-xl h-[480px] sm:h-[420px]">
          {cards.map((card, i) => (
            <StackedCard
              key={card.id}
              card={card}
              index={i}
              total={cards.length}
              pinnedRatio={pinnedRatio}
              scrollYProgress={scrollYProgress}
            />
          ))}
        </div>

        {closer && (
          <motion.div
            style={{ opacity: closerOpacity, y: closerY }}
            className="mt-12 will-change-transform"
          >
            {closer}
          </motion.div>
        )}

        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-1.5" aria-hidden>
          {cards.map((_, i) => (
            <CardDot key={i} index={i} total={cards.length} pinnedRatio={pinnedRatio} scrollYProgress={scrollYProgress} />
          ))}
          <ChevronDown className="w-3.5 h-3.5 text-muted-foreground/40 ml-2 animate-bounce" aria-hidden />
        </div>
      </div>
    </section>
  );
}
