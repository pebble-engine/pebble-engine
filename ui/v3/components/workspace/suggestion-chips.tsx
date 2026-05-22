"use client";

/**
 * SuggestionChips — Phase 50 (2026-05-22).
 *
 * Base44-style contextual suggestions under the iterate-input bar.
 * Shows quick-add chips for blocks the user is most likely to want
 * next ("Add testimonials", "Add pricing", "Add FAQ"). Each chip is
 * a real /api/blocks entry — click → calls insertBlock() and the
 * existing diff/toast flow kicks in.
 *
 * Why a focused 3-5 chip row instead of the full BlockGallery:
 *   - The gallery (~12+ blocks) is power-user surface (modal, scroll).
 *   - The chip row is a glance-and-click prompt. We pick the 4-5
 *     blocks most users want first, others stay one click away in the
 *     gallery via the "Browse all sections" link.
 *
 * Picks are static for now (curated by category importance). A future
 * iteration could pull the "what's missing from your site" signal
 * from the build integrity check and prioritise dynamically.
 */

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";
import { listBlocks, type BlockListing } from "@/lib/api";
import { interactions } from "@/lib/interactions";
import { type } from "@/lib/type";

// Block IDs that ALMOST every site benefits from. Order matters: most
// universally useful first, narrower further down. Anything past the
// first 4-5 stays one click away in the BlockGallery modal.
const PRIORITY_BLOCK_IDS: readonly string[] = [
  "testimonials",
  "pricing",
  "faq",
  "stats",
  "newsletter",
  "team",
  "logos",
  "cta",
];

export function SuggestionChips({
  busyBlockId,
  onInsert,
  onBrowseAll,
}: {
  /** ID of a block currently being inserted (disables the row). */
  busyBlockId: string | null;
  /** Click handler — wired to the parent's insertBlock flow. */
  onInsert: (blockId: string) => void;
  /** Optional handler for the "Browse all sections" link → opens BlockGallery. */
  onBrowseAll?: () => void;
}) {
  const [blocks, setBlocks] = useState<BlockListing[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    listBlocks()
      .then(({ blocks: all }) => {
        // Filter to the priority list, preserving priority order. Drop any
        // block ID the engine doesn't actually serve (engine catalog can
        // shrink without breaking this UI).
        const byId = new Map(all.map((b) => [b.id, b]));
        const ordered = PRIORITY_BLOCK_IDS
          .map((id) => byId.get(id))
          .filter((b): b is BlockListing => !!b)
          .slice(0, 5);
        setBlocks(ordered);
      })
      .catch(() => setBlocks([]))
      .finally(() => setLoaded(true));
  }, []);

  // Don't render anything until we've made the network call. Empty state
  // (engine returned 0 priority blocks) collapses silently — no use
  // teasing chips that aren't there.
  if (!loaded) return null;
  if (blocks.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className="flex flex-wrap items-center justify-center gap-1.5 pointer-events-auto"
    >
      <span className={`${type.mono} text-muted-foreground/70 mr-1`}>Add:</span>
      {blocks.map((b) => {
        const isBusy = busyBlockId === b.id;
        const isDisabled = busyBlockId !== null;
        return (
          <button
            key={b.id}
            disabled={isDisabled}
            onClick={() => onInsert(b.id)}
            title={b.description}
            className={`${interactions.chip} inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-card border border-border text-xs font-semibold text-muted-foreground hover:text-foreground hover:border-foreground/40 disabled:opacity-50 disabled:cursor-wait`}
          >
            {isBusy && <Loader2 className="w-3 h-3 animate-spin" />}
            {b.label}
          </button>
        );
      })}
      {onBrowseAll && (
        <button
          onClick={onBrowseAll}
          disabled={busyBlockId !== null}
          className="ml-1 text-[11px] font-semibold text-muted-foreground/60 hover:text-foreground transition-colors underline-offset-2 hover:underline"
        >
          Browse all sections →
        </button>
      )}
    </motion.div>
  );
}
