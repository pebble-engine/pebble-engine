"use client";

/**
 * ShuffleGrid — Phase 40j (2026-05-21).
 *
 * Replaces the ken-burns BackgroundCarousel as the hero's "show, don't
 * tell" layer. Adapted from a 21st.dev prompt Marc liked. Pebble twist:
 * the 16 tiles are real Pebble-built sites from `public/templates-preview/`,
 * not generic Unsplash stock — so the grid IS the product proof.
 *
 * Mechanics:
 *   - 4×4 grid (16 tiles) randomly reshuffled every 3 seconds via
 *     framer-motion's `layout` animation. Each tile slides to its new
 *     slot with a 1.5s spring.
 *   - Full-bleed inside the hero. Cream gradient overlay sits ON TOP
 *     of it (rendered separately in welcome-phase, just like the old
 *     BackgroundCarousel) so the DetectiveInput + hero text stay legible.
 *   - 16 source images cherry-picked from the 21 PNGs in
 *     /public/templates-preview/ — the ones that read strongest at
 *     tile-size + cover the widest range of DNAs / industries.
 *
 * Why retire BackgroundCarousel here:
 *   - One image cycling slowly under text → reads as a single example.
 *   - 16 tiles constantly shuffling → reads as "Pebble can build *many*
 *     different things." Stronger product story for the hero moment.
 */

import { motion } from "framer-motion";
import { useEffect, useRef, useState, type ReactElement } from "react";

/** Cherry-picked 16 from the 21 PNGs in /public/templates-preview/.
    Mix of industries (kitchen, brokerage, beauty, garage, instructor,
    service pro, ink studio) × color variants so the grid feels diverse
    on every shuffle. */
const TILE_SRCS: string[] = [
  "/templates-preview/artisan_kitchen.png",
  "/templates-preview/artisan_kitchen_olive.png",
  "/templates-preview/boutique_brokerage.png",
  "/templates-preview/boutique_brokerage_navy.png",
  "/templates-preview/honest_garage.png",
  "/templates-preview/honest_garage_rust.png",
  "/templates-preview/ink_studio.png",
  "/templates-preview/ink_studio_oxblood.png",
  "/templates-preview/instructor_pro.png",
  "/templates-preview/instructor_pro_forest.png",
  "/templates-preview/luxe_beauty.png",
  "/templates-preview/luxe_beauty_aubergine.png",
  "/templates-preview/service_pro.png",
  "/templates-preview/service_pro_navy.png",
  "/templates-preview/artisan_kitchen_navy.png",
  "/templates-preview/instructor_pro_navy.png",
];

type Tile = { id: number; src: string };

const TILES: Tile[] = TILE_SRCS.map((src, i) => ({ id: i + 1, src }));

/** Fisher-Yates shuffle. Returns a new array; doesn't mutate the input. */
function shuffle<T>(input: T[]): T[] {
  const arr = [...input];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function renderSquares(tiles: Tile[]): ReactElement[] {
  return tiles.map((tile) => (
    <motion.div
      key={tile.id}
      layout
      transition={{ duration: 1.5, type: "spring" }}
      className="w-full h-full rounded-md overflow-hidden bg-muted will-change-transform"
      style={{
        backgroundImage:    `url(${tile.src})`,
        backgroundSize:     "cover",
        backgroundPosition: "center",
      }}
      aria-hidden
    />
  ));
}

/**
 * Standalone grid — usable on its own (e.g. side-by-side hero layout).
 * For the Pebble landing we use the full-bleed wrapper below, but this
 * stays exported in case we want a side-by-side variant later.
 */
export function ShuffleGrid({
  intervalMs = 3000,
  className = "",
}: {
  intervalMs?: number;
  className?: string;
}) {
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Phase 40m hydration fix (2026-05-21) — initial state MUST be
  // deterministic on the server. `Math.random()` during initial render
  // would render one order on the server and a different one on the
  // client → React hydration mismatch. So we render TILES in source
  // order on first paint, then trigger the first shuffle in a useEffect
  // (client-only). The user sees the source order for ~one tick before
  // the first random shuffle kicks in, then it shuffles every interval.
  const [tiles, setTiles] = useState<Tile[]>(TILES);

  useEffect(() => {
    // Phase 41 iOS perf (2026-05-21) — 16 concurrent spring-layout
    // animations every 3s is heavy on low-end iPhones. On screens
    // ≤640px (Tailwind sm breakpoint) we slow the cadence so the GPU
    // gets time to recover between shuffles. Saves Marc's iPhone from
    // turning into a hand-warmer; still visually alive.
    const isMobile = typeof window !== "undefined" && window.matchMedia("(max-width: 640px)").matches;
    const effectiveInterval = isMobile ? Math.max(intervalMs * 2, 6000) : intervalMs;

    // Immediate first shuffle on mount — no perceptible delay vs the
    // old behavior, but it happens AFTER hydration so server + client
    // markup match.
    setTiles(shuffle(TILES));
    const tick = () => {
      setTiles((cur) => shuffle(cur));
      timeoutRef.current = setTimeout(tick, effectiveInterval);
    };
    timeoutRef.current = setTimeout(tick, effectiveInterval);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [intervalMs]);

  return (
    <div
      className={`grid grid-cols-4 grid-rows-4 gap-1 ${className}`}
      aria-hidden
    >
      {renderSquares(tiles)}
    </div>
  );
}

/**
 * Full-bleed wrapper for use as a hero backdrop. Absolutely positioned
 * inside the relative hero `<section>`. Cream gradient overlay is NOT
 * baked in here — welcome-phase renders its own overlay on top of this
 * (same pattern the old BackgroundCarousel used) so the legibility
 * tuning lives next to the text it's protecting.
 */
export function ShuffleHeroBackdrop({ intervalMs = 3000 }: { intervalMs?: number }) {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      <ShuffleGrid
        intervalMs={intervalMs}
        className="absolute inset-0 h-full w-full p-2 sm:p-4"
      />
    </div>
  );
}

export default ShuffleHeroBackdrop;
