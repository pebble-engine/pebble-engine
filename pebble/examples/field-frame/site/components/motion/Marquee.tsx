"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/** Infinite horizontal marquee strip. Self-contained (framer-motion loop, no
 *  globals.css dependency). Decorative — children are duplicated for a seamless
 *  loop, so this is not an editable region. */
export default function Marquee({
  children,
  className,
  speed = 22,
}: {
  children: ReactNode;
  className?: string;
  speed?: number;
}) {
  const reduce = useReducedMotion();
  return (
    <div className={`flex overflow-hidden ${className ?? ""}`}>
      <motion.div
        className="flex shrink-0 gap-8 pr-8"
        animate={reduce ? undefined : { x: ["0%", "-50%"] }}
        transition={{ repeat: Infinity, ease: "linear", duration: speed }}
      >
        {children}
        {children}
      </motion.div>
    </div>
  );
}
