"use client";
import { useEffect, useState } from "react";

type Props = {
  text: string;
  charDelay?: number;     // ms between chars; default 30
  initialDelay?: number;  // ms before first char animates; default 200
  duration?: number;      // ms per char transition; default 500
  className?: string;
};

/**
 * Brand-tuned AnimatedHeading.
 *
 * Same a11y pattern as the engine's foundation component:
 *   - <span className="sr-only">{text}</span> for screen readers
 *   - <span aria-hidden="true"> wraps the decorative per-char animation
 *
 * Differences from the engine version:
 *   - No textShadow — Pebble's marketing site is on a LIGHT background
 *     (Sand #FAF8F3), so legibility is fine without scaffolding.
 *   - Default font weight tuned for editorial restraint (font-normal).
 */
export function AnimatedHeading({
  text,
  charDelay = 30,
  initialDelay = 200,
  duration = 500,
  className,
}: Props) {
  const [ready, setReady] = useState(false);
  const [reduce, setReduce] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const t = setTimeout(() => setReady(true), initialDelay);
    return () => clearTimeout(t);
  }, [initialDelay]);

  const lines = text.split("\n");
  return (
    <h1
      className={className}
      style={{ letterSpacing: "-0.03em" }}
    >
      <span className="sr-only">{text.replace(/\n/g, " ")}</span>
      <span aria-hidden="true">
        {lines.map((line, lineIndex) => {
          const lineOffset = lineIndex * line.length * charDelay;
          return (
            <span key={lineIndex} style={{ display: "block" }}>
              {Array.from(line).map((ch, charIndex) => {
                const delay = reduce ? 0 : lineOffset + charIndex * charDelay;
                return (
                  <span
                    key={charIndex}
                    style={{
                      display: "inline-block",
                      opacity: ready || reduce ? 1 : 0,
                      transform: ready || reduce ? "translateY(0)" : "translateY(8px)",
                      transition: `opacity ${duration}ms ease, transform ${duration}ms ease`,
                      transitionDelay: `${delay}ms`,
                    }}
                  >
                    {ch === " " ? " " : ch}
                  </span>
                );
              })}
            </span>
          );
        })}
      </span>
    </h1>
  );
}
