"use client";
import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/** Scroll-driven vertical drift. Wraps an image/child that keeps its own
 *  data-pebble-id; the wrapper holds no editable slot. Reduced-motion → static. */
export default function Parallax({
  children,
  className,
  distance = 60,
}: {
  children: ReactNode;
  className?: string;
  distance?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [distance, -distance]);
  return (
    <div ref={ref} className={className}>
      <motion.div style={{ y: reduce ? 0 : y }} className="h-full w-full">
        {children}
      </motion.div>
    </div>
  );
}
