"use client";

import { useCallback, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Building2, X } from "lucide-react";
import { BusinessKnowledgeCard } from "@/components/workspace/business-knowledge-card";
import { getProjectKnowledge, saveProjectKnowledge } from "@/lib/api";

/**
 * P1 — per-project "about this business" surface, on demand.
 *
 * A top-bar button that opens a right slide-over with the project knowledge
 * card. Kept off the edit preview surface (which is intentionally clutter-free)
 * — the owner opens it only when they want to.
 */
export function BusinessInfoButton({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);

  const load = useCallback(
    async () => (slug ? (await getProjectKnowledge(slug)).knowledge : ""),
    [slug],
  );
  const save = useCallback(
    async (t: string) => { if (slug) await saveProjectKnowledge(slug, t); },
    [slug],
  );

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        title="Tell Pebble about this business"
        aria-label="Business info"
        className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand"
      >
        <Building2 className="w-5 h-5" />
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              key="biz-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 bg-charcoal/20 z-40"
            />
            <motion.aside
              key="biz-panel"
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 24 }}
              transition={{ duration: 0.25 }}
              className="fixed top-16 bottom-0 right-0 w-full max-w-[420px] flex flex-col gap-4 p-5 bg-background border-l border-border overflow-y-auto z-50 shadow-[var(--shadow-2)]"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                  Business info
                </h2>
                <button
                  onClick={() => setOpen(false)}
                  aria-label="Close"
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-accent"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <BusinessKnowledgeCard
                title="Tell Pebble about this business"
                subtitle="Specific to this site. Pebble honors it on every build and edit here."
                load={load}
                save={save}
              />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
