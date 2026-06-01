"use client";
import { motion, useMotionValue, useReducedMotion } from "framer-motion";
import type { MouseEvent, ReactNode } from "react";

/** Hover-tilt 3D card. Wraps a card whose inner nodes keep their data-pebble-id
 *  (forwarded via ...rest). Reduced-motion → no tilt. */
export default function TiltCard({
  children,
  className,
  ...rest
}: {
  children: ReactNode;
  className?: string;
  [k: string]: unknown;
}) {
  const rx = useMotionValue(0);
  const ry = useMotionValue(0);
  const reduce = useReducedMotion();
  function onMove(e: MouseEvent<HTMLDivElement>) {
    if (reduce) return;
    const r = e.currentTarget.getBoundingClientRect();
    ry.set(((e.clientX - r.left) / r.width - 0.5) * 14);
    rx.set(-((e.clientY - r.top) / r.height - 0.5) * 14);
  }
  return (
    <motion.div
      onMouseMove={onMove}
      onMouseLeave={() => {
        rx.set(0);
        ry.set(0);
      }}
      style={{ rotateX: rx, rotateY: ry, transformPerspective: 800 }}
      className={`will-change-transform ${className ?? ""}`}
      {...rest}
    >
      {children}
    </motion.div>
  );
}
