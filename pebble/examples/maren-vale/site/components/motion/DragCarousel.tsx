"use client";
import { motion } from "framer-motion";
import type { ReactNode } from "react";

/** Horizontal drag/swipe row. Pass cards as children; each keeps its own
 *  data-pebble-id. Decorative drag only — no editable slot on the wrapper. */
export default function DragCarousel({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className={`overflow-hidden ${className ?? ""}`}>
      <motion.div
        drag="x"
        dragConstraints={{ left: -800, right: 0 }}
        className="flex cursor-grab gap-5 active:cursor-grabbing"
      >
        {children}
      </motion.div>
    </div>
  );
}
