"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/** Fade + rise into view. Transparent wrapper — the editable child keeps its
 *  own data-pebble-id (forwarded via ...rest). Reduced-motion → static. */
export default function FadeUp({
  children,
  className,
  ...rest
}: {
  children: ReactNode;
  className?: string;
  [k: string]: unknown;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
