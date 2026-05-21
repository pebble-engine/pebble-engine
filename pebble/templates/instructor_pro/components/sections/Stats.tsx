"use client";
import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { STATS } from "@/content/site";

/**
 * Four-column counter section per DNA notes — giant Outfit-black numerals
 * that count up via IntersectionObserver on scroll-into-view.
 */
export function Stats() {
  if (!STATS.length) return null;

  return (
    <section className="relative border-y border-border bg-card/30 py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4 sm:gap-6">
          {STATS.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.08, ease: "easeOut" }}
              className="text-center"
            >
              <CountUp value={stat.value} />
              <p className="mt-3 text-[11px] font-bold uppercase tracking-wide-15 text-subtle sm:text-xs">
                {stat.label}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

/**
 * Counts up from 0 to the numeric part of `value` when scrolled into view.
 * Preserves any suffix like "+" or "%" or trailing letters.
 */
function CountUp({ value }: { value: string }) {
  const [display, setDisplay] = useState("0");
  const ref = useRef<HTMLSpanElement | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    const numMatch = value.match(/\d+/);
    if (!numMatch) {
      setDisplay(value);
      return;
    }
    const target = parseInt(numMatch[0], 10);
    const suffix = value.slice(numMatch.index! + numMatch[0].length);
    const prefix = value.slice(0, numMatch.index!);

    const node = ref.current;
    if (!node) return;

    const reduceMotion = typeof window !== "undefined"
      && window.matchMedia
      && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    if (reduceMotion) {
      setDisplay(value);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !startedRef.current) {
            startedRef.current = true;
            const duration = 1400;
            const start = performance.now();
            const tick = (now: number) => {
              const elapsed = now - start;
              const progress = Math.min(elapsed / duration, 1);
              const eased = 1 - Math.pow(1 - progress, 3);
              const current = Math.round(target * eased);
              setDisplay(`${prefix}${current}${suffix}`);
              if (progress < 1) requestAnimationFrame(tick);
            };
            requestAnimationFrame(tick);
            observer.disconnect();
          }
        });
      },
      { threshold: 0.4 },
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [value]);

  return (
    <span
      ref={ref}
      className="font-display text-5xl font-black tracking-headline text-fg sm:text-6xl"
      aria-label={value}
    >
      {display}
    </span>
  );
}
