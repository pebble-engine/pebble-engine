"use client";
import { motion } from "framer-motion";
import { ReactNode } from "react";

type Direction = "up" | "down" | "left" | "right";

type Props = {
  children: ReactNode;
  direction?: Direction;
  delay?: number;
  duration?: number;
  className?: string;
};

const initial: Record<Direction, object> = {
  up:    { opacity: 0, y: 40 },
  down:  { opacity: 0, y: -40 },
  left:  { opacity: 0, x: 40 },
  right: { opacity: 0, x: -40 },
};

export function ScrollReveal({ children, direction = "up", delay = 0, duration = 0.7, className }: Props) {
  return (
    <motion.div
      initial={initial[direction]}
      whileInView={{ opacity: 1, x: 0, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration, ease: [0.16, 1, 0.3, 1], delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}