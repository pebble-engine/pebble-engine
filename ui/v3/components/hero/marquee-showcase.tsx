"use client";

/**
 * MarqueeShowcase — Phase 43.6 (2026-05-21).
 *
 * Replaces the §3 Looks palette-grid + hover preview (Phase 43 / 43.3)
 * with the vercel-v0-style reference Marc shared: a "Prompt →
 * Application" pill arc above a full-bleed horizontal marquee of real
 * Pebble template PNGs. Each tile is large enough to read as a real
 * artifact, not a thumbnail.
 *
 * Mechanics:
 *   • Pure CSS animation (translateX from 0 to -50%) on a flex track
 *     that contains the tile list TWICE — second copy provides the
 *     seamless wrap. No JS per-frame cost.
 *   • Pause on hover or keyboard focus so visitors can examine a
 *     specific template.
 *   • Pill arc: a Pebble-voiced spin on the reference. "A sentence"
 *     on the left (cream/sand pill, the input), "A real site" on the
 *     right (Pebble-blue gradient pill, the output). Connected by a
 *     thin border-color line.
 *   • Pebble dot-grid behind the marquee — subtle "designer's canvas"
 *     cue from the reference.
 *
 * The component is content-agnostic: pass in any list of {src, label}
 * tiles and it renders them. Default uses all 21 template PNGs from
 * /public/templates-preview/.
 */

import React from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export type ShowcaseTile = { src: string; label: string };

/** Default tile set — all 21 template PNGs in /public/templates-preview/.
    Order is hand-arranged to alternate color moods (dark / light / warm /
    cool) so the marquee doesn't visually clump. */
const DEFAULT_TILES: ShowcaseTile[] = [
  { src: "/templates-preview/artisan_kitchen.png",         label: "Artisan Kitchen" },
  { src: "/templates-preview/ink_studio_oxblood.png",      label: "Ink Studio" },
  { src: "/templates-preview/boutique_brokerage.png",      label: "Boutique Brokerage" },
  { src: "/templates-preview/honest_garage_rust.png",      label: "Honest Garage" },
  { src: "/templates-preview/luxe_beauty.png",             label: "Luxe Beauty" },
  { src: "/templates-preview/instructor_pro_forest.png",   label: "Instructor Pro" },
  { src: "/templates-preview/service_pro_navy.png",        label: "Service Pro" },
  { src: "/templates-preview/artisan_kitchen_olive.png",   label: "Artisan Kitchen · Olive" },
  { src: "/templates-preview/ink_studio.png",              label: "Ink Studio · Default" },
  { src: "/templates-preview/boutique_brokerage_sage.png", label: "Boutique Brokerage · Sage" },
  { src: "/templates-preview/honest_garage.png",           label: "Honest Garage · Default" },
  { src: "/templates-preview/luxe_beauty_aubergine.png",   label: "Luxe Beauty · Aubergine" },
  { src: "/templates-preview/instructor_pro.png",          label: "Instructor Pro · Default" },
  { src: "/templates-preview/service_pro_cream.png",       label: "Service Pro · Cream" },
  { src: "/templates-preview/artisan_kitchen_navy.png",    label: "Artisan Kitchen · Navy" },
  { src: "/templates-preview/ink_studio_steel.png",        label: "Ink Studio · Steel" },
  { src: "/templates-preview/boutique_brokerage_navy.png", label: "Boutique Brokerage · Navy" },
  { src: "/templates-preview/honest_garage_military.png",  label: "Honest Garage · Military" },
  { src: "/templates-preview/luxe_beauty_rose.png",        label: "Luxe Beauty · Rose" },
  { src: "/templates-preview/instructor_pro_navy.png",     label: "Instructor Pro · Navy" },
  { src: "/templates-preview/service_pro.png",             label: "Service Pro · Default" },
];

/* ----------------------------- pill arc ------------------------------ */

function PromptToSiteArc() {
  return (
    <div className="flex items-center justify-center gap-3 sm:gap-4">
      {/* Left pill — the input. Cream/sand with a subtle gradient shimmer. */}
      <motion.div
        initial={{ opacity: 0, x: -8 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="inline-flex items-center px-4 sm:px-5 py-1.5 sm:py-2 rounded-full text-sm sm:text-base font-medium tracking-tight"
        style={{
          background: "linear-gradient(135deg, #f7f3ec 0%, #ece6dc 100%)",
          color: "var(--color-foreground)",
          boxShadow: "0 1px 3px rgba(31,29,26,0.06), inset 0 1px 0 rgba(255,255,255,0.6)",
        }}
      >
        A sentence
      </motion.div>

      {/* Connector line */}
      <motion.div
        initial={{ scaleX: 0, opacity: 0 }}
        whileInView={{ scaleX: 1, opacity: 1 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
        className="h-px w-12 sm:w-24 bg-foreground/20 origin-left"
        aria-hidden
      />

      {/* Right pill — the output. Pebble-blue + warm gradient (matches
          the reference's "Application" pill which had a brand gradient). */}
      <motion.div
        initial={{ opacity: 0, x: 8 }}
        whileInView={{ opacity: 1, x: 0 }}
        viewport={{ once: true, amount: 0.5 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1], delay: 0.35 }}
        className="inline-flex items-center px-4 sm:px-5 py-1.5 sm:py-2 rounded-full text-sm sm:text-base font-semibold tracking-tight"
        style={{
          background: "linear-gradient(135deg, #c8d4e8 0%, #d8c4ee 35%, #f5d5b8 100%)",
          color: "var(--color-foreground)",
          boxShadow: "0 4px 14px rgba(48,84,255,0.18), inset 0 1px 0 rgba(255,255,255,0.7)",
        }}
      >
        A real site
      </motion.div>
    </div>
  );
}

/* ----------------------------- marquee --------------------------------- */

interface MarqueeShowcaseProps {
  tiles?: ShowcaseTile[];
  className?: string;
}

export function MarqueeShowcase({ tiles = DEFAULT_TILES, className = "" }: MarqueeShowcaseProps) {
  // Render the list TWICE so the CSS translateX(-50%) lands on the
  // same point in the second copy and the loop is seamless.
  const doubled = React.useMemo(() => [...tiles, ...tiles], [tiles]);

  return (
    <div className={cn("flex flex-col gap-8 sm:gap-12", className)}>
      <PromptToSiteArc />

      <div
        className="pebble-marquee relative w-full overflow-hidden"
        // Hide the hard edges with a soft gradient mask — left / right
        // tiles fade out so the marquee feels infinite, not clipped.
        style={{
          maskImage:
            "linear-gradient(to right, transparent 0%, black 6%, black 94%, transparent 100%)",
          WebkitMaskImage:
            "linear-gradient(to right, transparent 0%, black 6%, black 94%, transparent 100%)",
        }}
      >
        <div className="pebble-marquee-track flex gap-3 sm:gap-4 w-max">
          {doubled.map((tile, i) => (
            <div
              key={`${tile.src}-${i}`}
              tabIndex={0}
              aria-label={tile.label}
              title={tile.label}
              className={cn(
                "shrink-0 relative rounded-2xl overflow-hidden bg-card border border-border",
                "shadow-[0_8px_28px_rgba(31,29,26,0.08)]",
                // Tile size — wide aspect, taller on desktop so each
                // tile reads as a real screen instead of a thumbnail.
                "w-[260px] h-[340px] sm:w-[360px] sm:h-[460px] lg:w-[440px] lg:h-[560px]",
                "transition-shadow duration-300 hover:shadow-[0_16px_44px_rgba(31,29,26,0.16)]",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
              )}
            >
              <Image
                src={tile.src}
                alt={tile.label}
                fill
                sizes="(max-width: 640px) 260px, (max-width: 1024px) 360px, 440px"
                className="object-cover object-top"
                /* Lazy load — only the first ~3-5 are visible on initial
                   render; the rest load as the marquee scrolls. */
                loading={i < 5 ? "eager" : "lazy"}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MarqueeShowcase;
