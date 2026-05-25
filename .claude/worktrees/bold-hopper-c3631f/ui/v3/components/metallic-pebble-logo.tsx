"use client";

/**
 * MetallicPebbleLogo — animated CSS metallic "P" with light-ray background
 * and a repeating shine sweep. Pure CSS / Framer Motion — no images.
 *
 * Optionally renders a 3D image asset via `imageSrc` prop (e.g.
 * "/dashboard/metallic-p.png"). Falls back to the CSS metallic P on load
 * error or when `imageSrc` is omitted.
 *
 * Used in the dashboard empty state and potentially on /pricing and /landing.
 */

import { useState } from "react";
import { motion } from "framer-motion";

type Size = "sm" | "md" | "lg" | "xl";

const SIZE: Record<Size, { container: string; text: string }> = {
  sm: { container: "w-16 h-16", text: "text-[4.5rem]" },
  md: { container: "w-24 h-24", text: "text-[6.5rem]" },
  lg: { container: "w-32 h-32", text: "text-[9rem]" },
  xl: { container: "w-64 h-64 md:w-80 md:h-80", text: "text-[16rem] md:text-[20rem]" },
};

export type MetallicPebbleLogoProps = {
  size?: Size;
  className?: string;
  /** Optional rendered 3D image asset (e.g. "/dashboard/metallic-p.png").
   * If provided and loads successfully, renders the image instead of CSS P.
   * Falls back to CSS metallic P on load error. */
  imageSrc?: string;
};

export function MetallicPebbleLogo({
  size = "lg",
  className = "",
  imageSrc,
}: MetallicPebbleLogoProps) {
  const { container, text } = SIZE[size];
  const [imageErrored, setImageErrored] = useState(false);
  const useImage = imageSrc && !imageErrored;

  return (
    <div
      className={`relative flex items-center justify-center ${useImage ? "" : "overflow-hidden"} ${container} ${className}`}
      aria-hidden="true"
    >
      {useImage ? (
        /* eslint-disable-next-line @next/next/no-img-element */
        <img
          src={imageSrc}
          alt=""
          aria-hidden="true"
          className="w-full h-full object-contain"
          onError={() => setImageErrored(true)}
        />
      ) : (
        <>
      {/* ── Conic-gradient light rays (subtle radial burst) ── */}
      <div
        className="absolute inset-0"
        style={{
          background: `conic-gradient(
            from 0deg at 50% 50%,
            transparent 0deg,
            rgba(255,255,255,0.06) 15deg,
            transparent 30deg,
            rgba(255,255,255,0.04) 55deg,
            transparent 70deg,
            rgba(255,255,255,0.06) 90deg,
            transparent 105deg,
            rgba(255,255,255,0.04) 130deg,
            transparent 150deg,
            rgba(255,255,255,0.06) 175deg,
            transparent 190deg,
            rgba(255,255,255,0.04) 215deg,
            transparent 235deg,
            rgba(255,255,255,0.06) 260deg,
            transparent 275deg,
            rgba(255,255,255,0.04) 305deg,
            transparent 325deg,
            rgba(255,255,255,0.06) 350deg,
            transparent 360deg
          )`,
        }}
      />

      {/* ── Metallic "P" — gradient clipped to text ── */}
      <span
        role="presentation"
        className={`relative z-10 font-bold leading-none select-none ${text}`}
        style={{
          background:
            "linear-gradient(135deg, #888 0%, #ccc 18%, #f0f0f0 33%, #ddd 48%, #888 65%, #bbb 82%, #999 100%)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
          fontFamily: "Georgia, 'Times New Roman', serif",
        }}
      >
        P
      </span>

      {/* ── Animated shine sweep — GPU-composited translateX, no reflow ── */}
      <motion.div
        className="absolute top-0 bottom-0 w-1/2 pointer-events-none z-20"
        style={{
          background:
            "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.28) 50%, transparent 100%)",
        }}
        initial={{ x: "-100%" }}
        animate={{ x: ["-100%", "300%"] }}
        transition={{
          duration: 1.6,
          repeat: Infinity,
          repeatDelay: 4,
          ease: [0.22, 1, 0.36, 1],
        }}
      />
        </>
      )}
    </div>
  );
}
