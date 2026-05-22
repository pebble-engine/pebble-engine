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

/** Phase 43.12 (2026-05-22) — deterministic seeded shuffle. Marc
    reported the 4 marquee columns all showed the same tiles in the
    same order because we passed one array to each column. This
    shuffles per-column with a different seed so the streams visibly
    mix DIFFERENT tiles past the viewer at any given moment. Seeded
    instead of Math.random() so SSR + client render the same order
    (otherwise React hydration mismatches → blank cards). */
function shuffleSeeded<T>(arr: readonly T[], seed: number): T[] {
  const out = [...arr];
  let s = seed;
  for (let i = out.length - 1; i > 0; i--) {
    s = (s * 9301 + 49297) % 233280;
    const j = Math.floor((s / 233280) * (i + 1));
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}

export type DnaCardData = {
  label:   string;
  /** Optional — used as a fallback "swatch strip" if `preview` is missing. */
  colors?: readonly string[];
  feel:    string;
  /** Recommended — bg-image path. When present, the card renders the
      preview screenshot instead of the color swatches. */
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
          {(dna.colors ?? []).map((c, i) => (
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
  // Phase 43.12 — per-column shuffles. Each column gets the FULL tile
  // set but in a different order, so at any horizontal slice across
  // the 4 columns you see 4 DIFFERENT templates rather than 4 copies
  // of the same one. Seeds 1/2/3/4 are arbitrary; the only thing that
  // matters is they're distinct.
  const colA = React.useMemo(() => shuffleSeeded(dnas, 1), [dnas]);
  const colB = React.useMemo(() => shuffleSeeded(dnas, 2), [dnas]);
  const colC = React.useMemo(() => shuffleSeeded(dnas, 3), [dnas]);
  const colD = React.useMemo(() => shuffleSeeded(dnas, 4), [dnas]);
  const colMobile = React.useMemo(() => shuffleSeeded(dnas, 7), [dnas]);

  return (
    <>
      {/* DESKTOP — 3D 4-column vertical marquee. Hidden on mobile.
          Phase 43.10 (2026-05-22) — bumped perspective from 340px to
          900px so the 3D tilt actually reads (340 was nearly flat).
          Rotation angles also pushed slightly so the columns feel
          like they're falling toward the viewer at an angle rather
          than sitting in a flat row. */}
      <div
        className={cn(
          "hidden md:block",
          "relative h-[560px] lg:h-[640px] w-full overflow-hidden [perspective:900px] [perspective-origin:50%_50%]",
          className,
        )}
      >
        <div
          className="absolute inset-0 flex flex-row items-center justify-center gap-3 [transform-style:preserve-3d]"
          style={{
            transform:
              "translateZ(-120px) rotateX(22deg) rotateY(-14deg) rotateZ(20deg)",
          }}
        >
          <Marquee vertical pauseOnHover repeat={3} className="[--duration:42s] [--gap:0.75rem]">
            {colA.map((dna) => <DnaCard key={`a-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover reverse repeat={3} className="[--duration:38s] [--gap:0.75rem]">
            {colB.map((dna) => <DnaCard key={`b-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover repeat={3} className="[--duration:46s] [--gap:0.75rem]">
            {colC.map((dna) => <DnaCard key={`c-${dna.label}`} dna={dna} />)}
          </Marquee>
          <Marquee vertical pauseOnHover reverse repeat={3} className="[--duration:40s] [--gap:0.75rem]">
            {colD.map((dna) => <DnaCard key={`d-${dna.label}`} dna={dna} />)}
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
          {colMobile.map((dna) => <DnaCard key={`m-${dna.label}`} dna={dna} />)}
        </Marquee>
        <div className="pointer-events-none absolute inset-x-0 top-0    h-1/4 bg-gradient-to-b from-background to-transparent" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-1/4 bg-gradient-to-t from-background to-transparent" />
      </div>
    </>
  );
}

export default DnaMarquee;
