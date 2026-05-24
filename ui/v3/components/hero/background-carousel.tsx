"use client";

/**
 * BackgroundCarousel — Phase 40 (2026-05-21).
 *
 * The hero's "show, don't tell" layer. Auto-scrolls through real
 * Pebble-built site previews (the templates-gallery PNGs) behind the
 * hero text. Each slide gets a 7s display with slow ken-burns scale
 * + crossfade. Captions in the bottom-left identify the DNA + industry
 * so visitors learn what Pebble produces without reading marketing copy.
 *
 * Visual treatment:
 *   - Light-mode tuned: cream gradient overlay (60-75% opacity, no muddy
 *     blacks). Text on top of carousel must still read at WCAG-AA.
 *   - Ken-burns: slow 8s scale 1 → 1.04, opacity 0 → 1 → 0.
 *   - Caption: small eyebrow + display name, dark text on cream-tinted
 *     blur pill.
 *
 * The slide list is hardcoded to a curated 8 (not all 21 PNGs) — we
 * pick the ones that look strongest as backdrop and span industries.
 */

import { useEffect, useState } from "react";
import { AnimatePresence, motion, MotionConfig } from "framer-motion";
import { type } from "@/lib/type";

type Slide = {
  src:     string;
  label:   string;   // displayed name
  dna:     string;   // DNA card label
  industry: string;  // short industry descriptor
};

const SLIDES: Slide[] = [
  { src: "/templates-preview/artisan_kitchen.png", label: "Artisan Kitchen",       dna: "Garden Press",        industry: "Restaurant · Cafe" },
  { src: "/templates-preview/boutique_brokerage.png", label: "Boutique Brokerage", dna: "Marina",              industry: "Real Estate" },
  { src: "/templates-preview/ink_studio_oxblood.png", label: "Ink Studio",         dna: "Velvet Lounge",       industry: "Tattoo · Art Studio" },
  { src: "/templates-preview/luxe_beauty_aubergine.png", label: "Luxe Beauty",     dna: "Postmodern Max",      industry: "Salon · Beauty" },
  { src: "/templates-preview/service_pro_navy.png",  label: "Service Pro",        dna: "Industrial Freight",   industry: "Contractor · Services" },
  { src: "/templates-preview/cinematic_hero.png",     label: "Cinematic Hero",    dna: "Cinematic Light",      industry: "Service business" },
  { src: "/templates-preview/instructor_pro_forest.png", label: "Instructor Pro", dna: "Swiss Magazine",       industry: "Coach · Educator" },
  { src: "/templates-preview/artisan_kitchen_olive.png", label: "Artisan Kitchen — Olive", dna: "Garden Press", industry: "Restaurant · Cafe" },
];

const SLIDE_MS = 7000;

export function BackgroundCarousel() {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => {
      setIdx((i) => (i + 1) % SLIDES.length);
    }, SLIDE_MS);
    return () => window.clearInterval(id);
  }, []);

  const slide = SLIDES[idx];

  return (
    /* Phase 40d (2026-05-21) — override reducedMotion at the carousel
       level too. The carousel IS the product demo; it should run even
       when OS-level reduce-motion is on. App/workspace surfaces still
       respect the user pref. */
    <MotionConfig reducedMotion="never">
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {/* Slide image (ken-burns scale) */}
      <AnimatePresence mode="sync">
        <motion.div
          key={slide.src}
          initial={{ opacity: 0, scale: 1.0 }}
          animate={{ opacity: 1, scale: 1.04 }}
          exit={{ opacity: 0, scale: 1.06 }}
          transition={{
            opacity: { duration: 1.2, ease: [0.22, 1, 0.36, 1] },
            scale:   { duration: 8.0, ease: "linear" },
          }}
          className="absolute inset-0 will-change-transform"
          style={{
            backgroundImage:    `url(${slide.src})`,
            backgroundSize:     "cover",
            backgroundPosition: "center",
          }}
          aria-hidden
        />
      </AnimatePresence>

      {/* Cream gradient overlay — keeps the carousel as BACKGROUND, not
          competing for attention with the hero text. Strongest at top
          + bottom to vignette into the page chrome. */}
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-b from-background/85 via-background/70 to-background/90"
      />
      <div
        aria-hidden
        className="absolute inset-0 bg-gradient-to-r from-background/30 via-transparent to-background/30"
      />

      {/* Caption — bottom-left, small frosted pill */}
      <div className="absolute bottom-8 left-8 flex items-center gap-3 pointer-events-auto">
        <AnimatePresence mode="wait">
          <motion.div
            key={slide.src + "-caption"}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-card/80 backdrop-blur-md border border-border shadow-[0_4px_24px_rgba(0,0,0,0.04)]"
          >
            <span className={`${type.eyebrow}`}>
              {slide.dna}
            </span>
            <span aria-hidden className="w-px h-3 bg-border" />
            <span className={`${type.caption} !text-foreground/85`}>
              {slide.industry}
            </span>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Progress dots — bottom-right, subtle */}
      <div
        aria-hidden
        className="absolute bottom-8 right-8 hidden md:flex items-center gap-1.5"
      >
        {SLIDES.map((_, i) => (
          <span
            key={i}
            className={`w-1.5 h-1.5 rounded-full transition-colors duration-300 ${
              i === idx ? "bg-foreground/60" : "bg-foreground/15"
            }`}
          />
        ))}
      </div>
    </div>
    </MotionConfig>
  );
}
