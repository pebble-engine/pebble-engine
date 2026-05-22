"use client";

/**
 * Marquee — Phase 43.8 (2026-05-22).
 *
 * Generic infinite scrolling marquee. Pulled in for the §3 Looks
 * 3D-marquee redesign (Marc picked option A: same 21st.dev pattern,
 * different content — DNA cards instead of the original testimonials).
 * Lives in `components/ui/` because it's a primitive that could be
 * reused elsewhere (e.g. when real testimonials land in §5).
 *
 * Driven by CSS animations (no rAF), so the only JS cost is the React
 * render. Two CSS-vars control timing + gap:
 *   --duration: how long one full loop takes (e.g. `40s`)
 *   --gap:      space between repeated copies
 *
 * Both animations (`animate-marquee` horizontal + `animate-marquee-
 * vertical`) live in app/globals.css.
 */

import React, { ComponentPropsWithoutRef, useRef } from "react";
import { cn } from "@/lib/utils";

interface MarqueeProps extends ComponentPropsWithoutRef<"div"> {
  /** Custom class on the outer container. */
  className?: string;
  /** Reverse the animation direction. */
  reverse?: boolean;
  /** Pause animation when the marquee (or any of its ancestors via group) is hovered. */
  pauseOnHover?: boolean;
  /** Marquee content — typically a list of cards. */
  children: React.ReactNode;
  /** Animate vertically instead of horizontally. */
  vertical?: boolean;
  /** How many times to repeat the children for the seamless loop. */
  repeat?: number;
  ariaLabel?: string;
  ariaLive?: "off" | "polite" | "assertive";
  ariaRole?: string;
}

export function Marquee({
  className,
  reverse = false,
  pauseOnHover = false,
  children,
  vertical = false,
  repeat = 4,
  ariaLabel,
  ariaLive = "off",
  ariaRole = "marquee",
  ...props
}: MarqueeProps) {
  const marqueeRef = useRef<HTMLDivElement>(null);

  return (
    <div
      {...props}
      ref={marqueeRef}
      data-slot="marquee"
      className={cn(
        "group flex overflow-hidden p-2 [--duration:40s] [--gap:1rem] [gap:var(--gap)]",
        {
          "flex-row": !vertical,
          "flex-col": vertical,
        },
        className,
      )}
      aria-label={ariaLabel}
      aria-live={ariaLive}
      role={ariaRole}
      tabIndex={0}
    >
      {Array.from({ length: repeat }, (_, i) => (
        <div
          key={i}
          className={cn(
            !vertical ? "flex-row [gap:var(--gap)]" : "flex-col [gap:var(--gap)]",
            "flex shrink-0 justify-around",
            !vertical && "animate-marquee flex-row",
            vertical && "animate-marquee-vertical flex-col",
            pauseOnHover && "group-hover:[animation-play-state:paused]",
            reverse && "[animation-direction:reverse]",
          )}
        >
          {children}
        </div>
      ))}
    </div>
  );
}

export default Marquee;
