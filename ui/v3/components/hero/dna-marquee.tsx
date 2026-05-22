"use client";

/**
 * DnaMarquee — Phase 43.8 (2026-05-22).
 *
 * §3 Looks section, option A from the conversation: re-uses the
 * 21st.dev 3D vertical 4-column marquee pattern but renders DNA cards
 * (palette + name) instead of the original testimonials. The form
 * factor — narrow portrait-ish cards in vertical columns — fits the
 * DNA preview content way better than it fits landscape website
 * screenshots.
 *
 * Desktop: 4 vertical marquee columns with alternating directions,
 * tilted into 3D space (rotateX/Y/Z perspective). All 8 DNAs ride
 * through each column independently; cards pause on hover so the
 * visitor can examine one.
 *
 * Mobile (≤md): the 3D 4-column setup doesn't survive the iPhone
 * viewport — it'd be 4 illegible slivers. Falls back to a stacked
 * single-column auto-scroll list instead. Same content, sensible
 * layout, no perspective.
 */

import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Marquee } from "@/components/ui/marquee";

export type DnaCardData = {
  label:   string;
  colors:  readonly string[];
  feel:    string;
  preview?: string;
};

/* ----------------------------- card ---------------------------------- */

function DnaCard({ dna }: { dna: DnaCardData }) {
  return (
    <motion.div
      whileHover={{ scale: 1.04 }}
      transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "w-44 rounded-xl bg-card border border-border overflow-hidden",
        "shadow-[0_4px_18px_rgba(31,29,26,0.06)] hover:shadow-[0_12px_36px_rgba(31,29,26,0.14)]",
        "transition-shadow duration-200 cursor-default",
      )}
    >
      {/* Template preview — real Pebble site rendered in this DNA.
          Phase 43.9 — replaced the 4-swatch palette strip with the
          actual template screenshot Marc has mapped to each DNA.
          aspect-[16/10] keeps every card the same height; bg-top so
          the hero/nav of each template stays visible at the small
          render size. Falls back to a muted color block if a DNA
          somehow has no preview field. */}
      {dna.preview ? (
        <div
          className="aspect-[16/10] w-full bg-muted bg-cover bg-top"
          style={{ backgroundImage: `url(${dna.preview})` }}
          aria-hidden
        />
      ) : (
        <div className="flex h-14 w-full" aria-hidden>
          {dna.colors.map((c, i) => (
            <div key={i} className="flex-1" style={{ backgroundColor: c }} />
          ))}
        </div>
      )}
      <div className="p-3">
        <h3 className="text-sm font-semibold text-foreground leading-tight">{dna.label}</h3>
        <p className="text-[11px] text-muted-foreground mt-1 line-clamp-1">{dna.feel}</p>
      </div>
    </motion.div>
  );
}

/* ----------------------------- main ---------------------------------- */

interface DnaMarqueeProps {
  dnas: readonly DnaCardData[];
  className?: string;
}

export function DnaMarquee({ dnas, className = "" }: DnaMarqueeProps) {
  return (
    <>
      {/* DESKTOP — 3D 4-column vertical marquee. Hidden on mobile.
          Wrapped in [perspective:300px] container so the inner
          transform tilts in genuine 3D, not just a flat 2D shear. */}
      <div
        className={cn(
          "hidden md:block",
          "relative h-[560px] lg:h-[640px] w-full overflow-hidden [perspective:340px]",
          className,
        )}
      >
        <div
          className="absolute inset-0 flex flex-row items-center justify-center gap-3"
          style={{
            transform:
              "translateX(-40px) translateY(0px) translateZ(-100px) rotateX(18deg) rotateY(-12deg) rotateZ(18deg)",
          }}
        >
          <Marquee vertical pauseOnHover repeat={3} className="[--duration:42s] [--gap:0.75rem]">
            {dnas.map((dna) => <DnaCard key={`a-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover reverse repeat={3} className="[--duration:38s] [--gap:0.75rem]">
            {dnas.map((dna) => <DnaCard key={`b-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover repeat={3} className="[--duration:46s] [--gap:0.75rem]">
            {dnas.map((dna) => <DnaCard key={`c-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover reverse repeat={3} className="[--duration:40s] [--gap:0.75rem]">
            {dnas.map((dna) => <DnaCard key={`d-${dna.label}`} dna={dna} />)}
          </Marquee>
        </div>

        {/* Edge gradient overlays — fade the cards into the page bg
            at all 4 borders so the marquee feels infinite, not clipped. */}
        <div className="pointer-events-none absolute inset-x-0 top-0    h-1/4 bg-gradient-to-b from-background to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/4 bg-gradient-to-t from-background to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 left-0   w-1/5 bg-gradient-to-r from-background to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0  w-1/5 bg-gradient-to-l from-background to-transparent" />
      </div>

      {/* MOBILE — single-column auto-scrolling vertical marquee.
          Drops the 3D perspective + 4-column layout (both would be
          illegible on iPhone). Same DnaCards, single stream, faster
          duration so the user gets through them in reasonable time. */}
      <div className="md:hidden relative h-[420px] w-full overflow-hidden">
        <Marquee vertical pauseOnHover repeat={2} className="[--duration:26s] [--gap:0.75rem] items-center justify-center">
          {dnas.map((dna) => <DnaCard key={`m-${dna.label}`} dna={dna} />)}
        </Marquee>
        <div className="pointer-events-none absolute inset-x-0 top-0    h-1/4 bg-gradient-to-b from-background to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/4 bg-gradient-to-t from-background to-transparent" />
      </div>
    </>
  );
}

export default DnaMarquee;
