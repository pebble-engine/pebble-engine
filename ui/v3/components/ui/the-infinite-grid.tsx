"use client";

import React, { useState, useRef } from "react";
import { cn } from "@/lib/utils";
import {
  motion,
  useMotionValue,
  useMotionTemplate,
  useAnimationFrame,
  type MotionValue,
} from "framer-motion";

/**
 * Infinite Grid — a hero canvas that scrolls a faint grid behind a
 * cursor-revealed mask. From 21st.dev. Re-tuned for Pebble brand:
 * sage + river blur blobs instead of orange + blue.
 */
export const InfiniteGrid: React.FC<{
  className?: string;
  children?: React.ReactNode;
}> = ({ className, children }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const { left, top } = e.currentTarget.getBoundingClientRect();
    mouseX.set(e.clientX - left);
    mouseY.set(e.clientY - top);
  };

  const gridOffsetX = useMotionValue(0);
  const gridOffsetY = useMotionValue(0);

  // Slow drift — barely perceptible, but the eye picks it up.
  useAnimationFrame(() => {
    gridOffsetX.set((gridOffsetX.get() + 0.25) % 40);
    gridOffsetY.set((gridOffsetY.get() + 0.25) % 40);
  });

  const maskImage = useMotionTemplate`radial-gradient(360px circle at ${mouseX}px ${mouseY}px, black, transparent)`;

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className={cn(
        "relative w-full flex flex-col items-center justify-center overflow-hidden bg-background",
        className,
      )}
    >
      {/* Faint grid layer */}
      <div className="absolute inset-0 z-0 opacity-[0.06]">
        <GridPattern offsetX={gridOffsetX} offsetY={gridOffsetY} />
      </div>

      {/* Cursor-revealed active layer */}
      <motion.div
        className="absolute inset-0 z-0 opacity-50"
        style={{ maskImage, WebkitMaskImage: maskImage }}
      >
        <GridPattern offsetX={gridOffsetX} offsetY={gridOffsetY} />
      </motion.div>

      {/* Ambient color blobs — Pebble brand (sage + river, not orange + blue) */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute -right-[15%] -top-[20%] w-[45%] h-[45%] rounded-full bg-sage/25 blur-[140px]" />
        <div className="absolute right-[8%] top-[-8%] w-[22%] h-[22%] rounded-full bg-river/20 blur-[100px]" />
        <div className="absolute -left-[10%] -bottom-[20%] w-[40%] h-[40%] rounded-full bg-river/20 blur-[140px]" />
      </div>

      {children}
    </div>
  );
};

const GridPattern: React.FC<{
  offsetX: MotionValue<number>;
  offsetY: MotionValue<number>;
}> = ({ offsetX, offsetY }) => (
  <svg className="w-full h-full">
    <defs>
      <motion.pattern
        id="grid-pattern"
        width="40"
        height="40"
        patternUnits="userSpaceOnUse"
        x={offsetX}
        y={offsetY}
      >
        <path
          d="M 40 0 L 0 0 0 40"
          fill="none"
          stroke="currentColor"
          strokeWidth="1"
          className="text-graphite"
        />
      </motion.pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#grid-pattern)" />
  </svg>
);
