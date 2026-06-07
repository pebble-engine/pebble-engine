"use client";

import { useCallback, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Sparkles, X, Loader2, Check } from "lucide-react";
import { listSkills, refine, type Skill, type RefinementId } from "@/lib/api";

type RowState = "idle" | "running" | "done" | "error";

/**
 * P2 — curated "Power moves" (skills), on demand.
 *
 * Top-bar button that opens a right slide-over listing Pebble's curated skills.
 * Each runs through the existing refine path (refine(slug, id)). Kept off the
 * clutter-free edit surface; surfaced only on click.
 */
export function PowerMovesButton({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);
  const [skills, setSkills] = useState<Skill[] | null>(null);
  const [state, setState] = useState<Record<string, RowState>>({});

  useEffect(() => {
    if (!open || skills) return;
    listSkills()
      .then((r) => setSkills(r.skills))
      .catch(() => setSkills([]));
  }, [open, skills]);

  const run = useCallback(async (id: string) => {
    if (!slug) return;
    setState((s) => ({ ...s, [id]: "running" }));
    try {
      await refine(slug, id as RefinementId);
      setState((s) => ({ ...s, [id]: "done" }));
      setTimeout(() => setState((s) => ({ ...s, [id]: "idle" })), 2500);
    } catch {
      setState((s) => ({ ...s, [id]: "error" }));
    }
  }, [slug]);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        title="Power moves"
        aria-label="Power moves"
        className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand"
      >
        <Sparkles className="w-5 h-5" />
      </button>

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              key="pm-backdrop"
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 bg-charcoal/20 z-40"
            />
            <motion.aside
              key="pm-panel"
              initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 24 }}
              transition={{ duration: 0.25 }}
              className="fixed top-16 bottom-0 right-0 w-full max-w-[420px] flex flex-col gap-4 p-5 bg-background border-l border-border overflow-y-auto z-50 shadow-[var(--shadow-2)]"
            >
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-mono uppercase tracking-widest text-muted-foreground">
                  Power moves
                </h2>
                <button onClick={() => setOpen(false)} aria-label="Close"
                  className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-accent">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <p className="text-sm text-muted-foreground -mt-1">
                One-click improvements. Pebble applies them to this site.
              </p>

              {skills === null && (
                <p className="text-sm text-muted-foreground">Loading…</p>
              )}
              {skills?.length === 0 && (
                <p className="text-sm text-muted-foreground">No power moves available.</p>
              )}

              <div className="flex flex-col gap-2">
                {skills?.map((sk) => {
                  const st = state[sk.id] ?? "idle";
                  return (
                    <button
                      key={sk.id}
                      onClick={() => run(sk.id)}
                      disabled={st === "running"}
                      className="text-left rounded-xl border border-border bg-card p-4 hover:bg-accent/50 transition-colors disabled:opacity-60"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-foreground">{sk.label}</span>
                        <span className="shrink-0 text-xs text-muted-foreground flex items-center gap-1">
                          {st === "running" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                          {st === "done" && <><Check className="w-3.5 h-3.5 text-green-600" /> Applied</>}
                          {st === "error" && <span className="text-destructive">Failed — retry</span>}
                          {st === "idle" && (sk.billable ? "uses 1 credit" : "free")}
                        </span>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{sk.description}</p>
                    </button>
                  );
                })}
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
