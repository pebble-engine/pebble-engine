"use client";
import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/** Cascade children into view. Wrap a list/grid container in <Stagger> and each
 *  item in <StaggerItem> (which forwards data-pebble-id via ...rest). */
export function Stagger({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.2 }}
      variants={{ show: { transition: { staggerChildren: 0.12 } } }}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({
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
      variants={
        reduce
          ? undefined
          : {
              hidden: { opacity: 0, y: 40 },
              show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } },
            }
      }
      {...rest}
    >
      {children}
    </motion.div>
  );
}

export default Stagger;
