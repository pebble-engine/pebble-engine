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

function cardWindow(index: number, total: number): {
  fadeIn:   [number, number];
  fadeOut:  [number, number];
  scaleIn:  [number, number];
  scaleOut: [number, number];
  yIn:      [number, number];
} {
  const HEADING_RESERVE = 0.12;
  const CLOSER_RESERVE  = 0.12;
  const usable          = 1 - HEADING_RESERVE - CLOSER_RESERVE;
  const cardSpan        = usable / total;
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
  scrollYProgress,
}: {
  card:            StackCard;
  index:           number;
  total:           number;
  scrollYProgress: MotionValue<number>;
}) {
  const w = cardWindow(index, total);
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

  const headingOpacity = useTransform(scrollYProgress, [0, 0.08], [0, 1]);
  const headingY       = useTransform(scrollYProgress, [0, 0.08], [48, 0]);
  const headingScale   = useTransform(scrollYProgress, [0, 0.08], [0.88, 1]);

  const closerOpacity  = useTransform(scrollYProgress, [0.88, 0.98], [0, 1]);
  const closerY        = useTransform(scrollYProgress, [0.88, 0.98], [24, 0]);

  const totalVh = cards.length * 100 + 60;

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
            <CardDot key={i} index={i} total={cards.length} scrollYProgress={scrollYProgress} />
          ))}
          <ChevronDown className="w-3.5 h-3.5 text-muted-foreground/40 ml-2 animate-bounce" aria-hidden />
        </div>
      </div>
    </section>
  );
}
