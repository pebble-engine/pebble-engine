"use client";
import { motion, useMotionValue, useReducedMotion } from "framer-motion";
import type { MouseEvent, ReactNode } from "react";

/** CTA whose link follows the cursor slightly. EDIT-SAFE: renders an <a> that
 *  keeps its editable label (children) and href; data-pebble-id rides via
 *  ...rest. Reduced-motion → static. */
export default function MagneticButton({
  children,
  href = "#",
  className,
  ...rest
}: {
  children: ReactNode;
  href?: string;
  className?: string;
  [k: string]: unknown;
}) {
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const reduce = useReducedMotion();
  function onMove(e: MouseEvent<HTMLAnchorElement>) {
    if (reduce) return;
    const r = e.currentTarget.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * 0.35);
    y.set((e.clientY - (r.top + r.height / 2)) * 0.35);
  }
  return (
    <motion.a
      href={href}
      onMouseMove={onMove}
      onMouseLeave={() => {
        x.set(0);
        y.set(0);
      }}
      style={{ x, y }}
      whileTap={{ scale: 0.96 }}
      className={className}
      {...rest}
    >
      {children}
    </motion.a>
  );
}
