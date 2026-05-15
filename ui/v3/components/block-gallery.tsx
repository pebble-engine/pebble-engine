"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  X,
  Loader2,
  BarChart3,
  Coins,
  Grid3x3,
  HelpCircle,
  MessageSquareQuote,
  Rocket,
  Square,
  type LucideIcon,
} from "lucide-react";
import { listBlocks, type BlockListing } from "@/lib/api";

/**
 * Block Gallery — the catalog of DNA-themed drop-in sections.
 *
 * Opens as a modal from the workspace. Lists every block returned by
 * GET /api/blocks, grouped by category, with the DNA-aware promise:
 * "everything in here re-themes against YOUR site's DNA when inserted".
 *
 * On click, the parent owns the insertion call so it can refresh the
 * preview iframe + toast a snapshot id (for undo). This component only
 * picks; it does not insert.
 */

// Map server-supplied icon NAMES onto actual Lucide components. Keep
// this small — the server's catalog deliberately uses well-known names.
const ICON_MAP: Record<string, LucideIcon> = {
  MessageSquareQuote,
  Coins,
  HelpCircle,
  Grid3x3,
  Rocket,
  BarChart3,
};

const CATEGORY_LABELS: Record<string, string> = {
  "social-proof":  "Social proof",
  "monetization":  "Monetization",
  "explainer":     "Explain what you do",
  "conversion":    "Conversion",
  "growth":        "Growth",
};

type Props = {
  open:        boolean;
  busyBlockId: string | null;
  onClose:     () => void;
  onInsert:    (blockId: string) => void;
};

export function BlockGallery({ open, busyBlockId, onClose, onInsert }: Props) {
  const [blocks, setBlocks] = useState<BlockListing[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Lazy-load the catalog the first time the gallery opens. The list is
  // tiny and never changes during a session, so we cache it locally.
  useEffect(() => {
    if (!open || blocks !== null) return;
    void (async () => {
      try {
        const data = await listBlocks();
        setBlocks(data.blocks);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Couldn't load blocks");
      }
    })();
  }, [open, blocks]);

  // Close on Escape — modal accessibility table stakes.
  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  // Group blocks by category for the gallery layout.
  const grouped = blocks
    ? blocks.reduce<Record<string, BlockListing[]>>((acc, b) => {
        const cat = b.category || "other";
        if (!acc[cat]) acc[cat] = [];
        acc[cat].push(b);
        return acc;
      }, {})
    : null;

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={onClose}
          role="dialog"
          aria-modal="true"
          aria-labelledby="block-gallery-title"
        >
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 16, scale: 0.98 }}
            transition={{ duration: 0.25 }}
            className="bg-card rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col border border-border"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between p-6 border-b border-border">
              <div>
                <h2 id="block-gallery-title" className="font-display text-2xl font-semibold text-foreground">
                  Add a section
                </h2>
                <p className="text-sm text-muted-foreground mt-1">
                  Every block re-themes against your site&apos;s DNA on insert. Free —
                  no credits used.
                </p>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close"
                className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {error && (
                <p className="text-sm text-destructive">{error}</p>
              )}
              {!blocks && !error && (
                <div className="flex items-center justify-center py-12 text-muted-foreground">
                  <Loader2 className="w-5 h-5 animate-spin" />
                </div>
              )}
              {grouped &&
                Object.entries(grouped).map(([category, items]) => (
                  <section key={category} className="mb-8 last:mb-0">
                    <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground mb-3">
                      {CATEGORY_LABELS[category] || category}
                    </h3>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                      {items.map((block) => {
                        const Icon = ICON_MAP[block.icon] || Square;
                        const isBusy = busyBlockId === block.id;
                        return (
                          <button
                            type="button"
                            key={block.id}
                            disabled={isBusy || busyBlockId !== null}
                            onClick={() => onInsert(block.id)}
                            className="text-left bg-background border border-border rounded-xl p-4 hover:border-secondary hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-wait flex flex-col gap-2 group"
                          >
                            <div className="flex items-center gap-2">
                              <span className="w-8 h-8 rounded-lg bg-secondary/15 text-secondary flex items-center justify-center group-hover:bg-secondary group-hover:text-white transition-colors">
                                {isBusy ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Icon className="w-4 h-4" />
                                )}
                              </span>
                              <span className="font-semibold text-sm text-foreground">{block.label}</span>
                            </div>
                            <p className="text-xs text-muted-foreground leading-snug">
                              {block.description}
                            </p>
                          </button>
                        );
                      })}
                    </div>
                  </section>
                ))}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
