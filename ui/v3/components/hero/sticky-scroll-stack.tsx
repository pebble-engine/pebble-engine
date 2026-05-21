"use client";

/**
 * StickyScrollStack — Phase 40e (2026-05-21).
 *
 * Apple iPad / Linear / Vercel sticky-scroll stack pattern. The section
 * pins to the top of the viewport while the user scrolls; cards stack on
 * top of each other progressively as scroll progresses; the section
 * unpins when all cards have landed. Feels like the page is being
 * pulled UP toward the viewer.
 *
 * Mechanics:
 *   - Outer container is `relative` and TALL: ~`n × 100vh` where n is
 *     the number of cards. This provides the scroll distance.
 *   - Inner wrapper is `sticky top-0 h-screen`. While the outer container
 *     is in the viewport, the inner stays pinned to the top.
 *   - useScroll on the outer ref gives us scrollYProgress 0 → 1 across
 *     the entire pinned distance.
 *   - Each card maps its own opacity/scale/y range from scrollYProgress.
 *     Cards 0..n-1 enter sequentially. Once a card has entered, it
 *     RECEDES slightly (smaller scale + dim) as the next card lands on
 *     top — that's the "stacking" feel.
 *   - Final card stays in place at scrollYProgress=1.
 *
 * Optional `closer` slot renders after the last card has landed —
 * useful for "ready to build" CTAs that transition into the next section.
 */

import { useEffect, useRef, useState, type ReactNode } from "react";
import { motion, useScroll, useTransform, type MotionValue } from "framer-motion";
import { type } from "@/lib/type";
import { ChevronDown } from "lucide-react";

export type StackCard = {
  /** Unique id for React key. */
  id:    string;
  /** Lucide icon component or any React node rendered top-left. */
  icon?: ReactNode;
  /** Eyebrow text above the title (e.g. "Step 01"). Optional. */
  eyebrow?: string;
  /** Card title — uses type.heading.l. */
  title: string;
  /** Body paragraph. */
  body:  string;
  /** Optional accent text (e.g. a quoted detail) shown below body. */
  accent?: string;
};

type Props = {
  /** Cards to stack, top-to-bottom. Min 2, recommended 3-4. */
  cards: StackCard[];
  /** Section anchor id (for nav). */
  id?: string;
  /** Heading shown ABOVE the stack — uses type.display.l. */
  heading?: string;
  /** Optional subhead below the heading. */
  subhead?: string;
  /** Optional CTA shown after the final card lands. Renders inside the
      sticky frame at scrollYProgress=1. */
  closer?: ReactNode;
  /** className applied to the section element. */
  className?: string;
};

/** Per-card scroll progress window. Each card is fully visible at the
    midpoint of its window. */
function cardWindow(index: number, total: number): {
  fadeIn:  [number, number];  // opacity 0 → 1
  fadeOut: [number, number];  // opacity 1 → 0.6 (recede)
  scaleIn: [number, number];  // scale 0.92 → 1
  scaleOut: [number, number]; // scale 1 → 0.95 (recede)
  yIn:     [number, number];  // y 80 → 0
} {
  // Reserve 12% of total scroll for heading entrance + 12% for closer
  // exit; cards stack within the remaining 76%.
  const HEADING_RESERVE = 0.12;
  const CLOSER_RESERVE  = 0.12;
  const usable          = 1 - HEADING_RESERVE - CLOSER_RESERVE;
  const cardSpan        = usable / total;
  const start           = HEADING_RESERVE + index * cardSpan;
  const fadeInEnd       = start + cardSpan * 0.55;        // 55% of card's span is "entering"
  const fadeOutStart    = start + cardSpan * 0.85;        // last 15% is "receding"
  const fadeOutEnd      = start + cardSpan * 1.0;
  return {
    fadeIn:   [start, fadeInEnd],
    fadeOut:  [fadeOutStart, fadeOutEnd],
    scaleIn:  [start, fadeInEnd],
    scaleOut: [fadeOutStart, fadeOutEnd],
    yIn:      [start, fadeInEnd],
  };
}

/** A single stacked card. Reads the parent's scrollYProgress and computes
    its own opacity/scale/y based on its index. */
function StackedCard({
  card,
  index,
  total,
  scrollYProgress,
}: {
  card:            StackCard;
  index:           number;
  total:           number;
  scrollYProgress: MotionValue<number>;
}) {
  const w = cardWindow(index, total);
  const isLast = index === total - 1;

  // Opacity: 0 → 1 entering, then stays 1 (no fade-out for the last card)
  const opacity = useTransform(
    scrollYProgress,
    isLast
      ? [w.fadeIn[0], w.fadeIn[1]]
      : [w.fadeIn[0], w.fadeIn[1], w.fadeOut[0], w.fadeOut[1]],
    isLast ? [0, 1] : [0, 1, 1, 0.55],
  );

  // Scale: 0.92 → 1 entering, 1 → 0.94 receding (last stays at 1)
  const scale = useTransform(
    scrollYProgress,
    isLast
      ? [w.scaleIn[0], w.scaleIn[1]]
      : [w.scaleIn[0], w.scaleIn[1], w.scaleOut[0], w.scaleOut[1]],
    isLast ? [0.92, 1] : [0.92, 1, 1, 0.94],
  );

  // Y: 80px → 0 entering. Once landed, slight upward drift while receding
  // gives the "card slid under" feel.
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

export function StickyScrollStack({
  cards,
  id,
  heading,
  subhead,
  closer,
  className = "",
}: Props) {
  const ref = useRef<HTMLElement>(null);
  // Phase 40e fix (2026-05-21) — gate useScroll's target on mount.
  // Framer Motion throws "Target ref is defined but not hydrated"
  // when useScroll fires during the SSR-to-CSR handoff before
  // ref.current is fully attached. By passing `undefined` until after
  // mount, useScroll falls back to document scroll (harmless — we
  // ignore the result before mount anyway), then switches to the
  // section-relative ref once the DOM is ready.
  const [mounted, setMounted] = useState(false);
  useEffect(() => { setMounted(true); }, []);
  const { scrollYProgress } = useScroll({
    target: mounted ? ref : undefined,
    offset: ["start start", "end end"],
  });

  // Heading enters in the first 12% of scroll progress.
  const headingOpacity = useTransform(scrollYProgress, [0, 0.08], [0, 1]);
  const headingY       = useTransform(scrollYProgress, [0, 0.08], [48, 0]);
  const headingScale   = useTransform(scrollYProgress, [0, 0.08], [0.88, 1]);

  // Closer enters in the last 12% (after final card has fully landed).
  const closerOpacity  = useTransform(scrollYProgress, [0.88, 0.98], [0, 1]);
  const closerY        = useTransform(scrollYProgress, [0.88, 0.98], [24, 0]);

  // Total height: 100vh per card + 60vh of overhead for heading entrance
  // and closer exit. Tuned by feel — adjust if the section feels too long.
  const totalVh = cards.length * 100 + 60;

  return (
    <section
      ref={ref}
      id={id}
      className={`relative ${className}`}
      style={{ height: `${totalVh}vh` }}
    >
      {/* Sticky inner: pins to viewport top while user scrolls through
          the tall outer container. */}
      <div className="sticky top-0 h-screen flex flex-col items-center justify-center px-4 max-w-6xl mx-auto overflow-hidden">
        {/* Heading + subhead — fades in early, stays through stack */}
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

        {/* Card stack container — cards overlap inside it */}
        <div className="relative w-full max-w-xl h-[480px] sm:h-[420px]">
          {cards.map((card, i) => (
            <StackedCard
              key={card.id}
              card={card}
              index={i}
              total={cards.length}
              scrollYProgress={scrollYProgress}
            />
          ))}
        </div>

        {/* Closer slot — fires after final card lands */}
        {closer && (
          <motion.div
            style={{ opacity: closerOpacity, y: closerY }}
            className="mt-12 will-change-transform"
          >
            {closer}
          </motion.div>
        )}

        {/* Scroll-progress dots, hint that there's more */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-1.5" aria-hidden>
          {cards.map((_, i) => (
            <CardDot key={i} index={i} total={cards.length} scrollYProgress={scrollYProgress} />
          ))}
          <ChevronDown className="w-3.5 h-3.5 text-muted-foreground/40 ml-2 animate-bounce" aria-hidden />
        </div>
      </div>
    </section>
  );
}

/** Tiny progress indicator dot. Lights up as the corresponding card lands. */
function CardDot({
  index,
  total,
  scrollYProgress,
}: {
  index:           number;
  total:           number;
  scrollYProgress: MotionValue<number>;
}) {
  const w = cardWindow(index, total);
  const opacity = useTransform(scrollYProgress, [w.fadeIn[0], w.fadeIn[1]], [0.15, 1]);
  return (
    <motion.span
      style={{ opacity }}
      className="block w-1.5 h-1.5 rounded-full bg-foreground"
    />
  );
}
