"use client";
import { ReactNode, useEffect, useState } from "react";

type Props = {
  children: ReactNode;
  delay?: number;    // ms before fade starts; default 0
  duration?: number; // ms transition; default 1000
  className?: string;
  as?: "div" | "section" | "article";
};

/**
 * Same simple opacity wrapper as the engine's FadeIn.
 * Respects prefers-reduced-motion. No translation — Pebble's brand
 * favors subtle, never aggressive motion (per brand book pattern #5).
 */
export function FadeIn({
  children,
  delay = 0,
  duration = 1000,
  className,
  as = "div",
}: Props) {
  const [visible, setVisible] = useState(false);
  const [reduce, setReduce] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduce(mq.matches);
    const t = setTimeout(() => setVisible(true), delay);
    return () => clearTimeout(t);
  }, [delay]);

  const style = {
    opacity: visible || reduce ? 1 : 0,
    transition: `opacity ${duration}ms ease`,
  };

  if (as === "section") return <section className={className} style={style}>{children}</section>;
  if (as === "article") return <article className={className} style={style}>{children}</article>;
  return <div className={className} style={style}>{children}</div>;
}
