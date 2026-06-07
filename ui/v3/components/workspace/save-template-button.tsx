"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { BookmarkPlus, Check, Loader2, X } from "lucide-react";
import { savePersonalTemplate } from "@/lib/api";

/**
 * P4 — "Save as template" from the workspace.
 *
 * A top-bar button that opens a small popover to name and save the CURRENT
 * project as a personal, reusable template. New projects can then be spun up
 * from it on the Templates page ("Your templates").
 */
export function SaveTemplateButton({
  slug,
  defaultLabel = "",
}: {
  slug: string;
  defaultLabel?: string;
}) {
  const [open, setOpen] = useState(false);
  const [label, setLabel] = useState(defaultLabel);
  const [state, setState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [error, setError] = useState<string | null>(null);
  const wrap = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: MouseEvent) => {
      if (wrap.current && !wrap.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    window.addEventListener("mousedown", onDown);
    window.addEventListener("keydown", onKey);
    return () => { window.removeEventListener("mousedown", onDown); window.removeEventListener("keydown", onKey); };
  }, [open]);

  const submit = async () => {
    const name = label.trim();
    if (!name) { setError("Give your template a name"); return; }
    setState("saving"); setError(null);
    try {
      await savePersonalTemplate(slug, name);
      setState("saved");
      setTimeout(() => setOpen(false), 1100);
    } catch (e) {
      setState("error");
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <div ref={wrap} className="relative">
      <button
        onClick={() => { setOpen((v) => !v); setState("idle"); setError(null); setLabel(defaultLabel); }}
        title="Save this site as a reusable template"
        aria-label="Save as template"
        className="w-10 h-10 rounded-full flex items-center justify-center text-graphite hover:text-charcoal dark:text-pebble dark:hover:bg-stone/40 dark:hover:text-sand"
      >
        <BookmarkPlus className="w-5 h-5" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.16 }}
            className="absolute right-0 top-12 z-50 w-72 rounded-2xl border border-border bg-card p-4 shadow-[var(--shadow-2)]"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <h3 className="text-sm font-semibold text-foreground">Save as template</h3>
                <p className="mt-0.5 text-xs text-muted-foreground">Reuse this site as a starting point for new projects.</p>
              </div>
              <button onClick={() => setOpen(false)} aria-label="Close" className="text-muted-foreground hover:text-foreground">
                <X className="w-4 h-4" />
              </button>
            </div>

            {state === "saved" ? (
              <div className="flex items-center gap-2 py-2 text-sm text-emerald-600 dark:text-emerald-400">
                <Check className="w-4 h-4" /> Saved to your templates
              </div>
            ) : (
              <>
                <input
                  type="text"
                  value={label}
                  autoFocus
                  onChange={(e) => setLabel(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") submit(); }}
                  placeholder="e.g. My pest-control layout"
                  className="w-full rounded-xl border border-border bg-background px-3 py-2 text-sm placeholder:text-muted-foreground/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                />
                {error && <p className="mt-1.5 text-xs text-destructive">{error}</p>}
                <button
                  onClick={submit}
                  disabled={state === "saving"}
                  className="mt-3 w-full inline-flex items-center justify-center gap-2 rounded-full bg-foreground px-4 py-2 text-sm font-medium text-background hover:bg-foreground/90 disabled:opacity-60"
                >
                  {state === "saving" && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {state === "saving" ? "Saving…" : "Save template"}
                </button>
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
