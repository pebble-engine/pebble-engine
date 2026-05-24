"use client";

/**
 * ReadyPhase — Phase 49 (2026-05-22).
 *
 * The completion moment. Sits between draft (build streaming) and
 * design (the editor). The previous flow snapped silently from "Done"
 * into the editor after a 600ms pause — Marc's Base44-inspired
 * critique: "the user just spent 90 seconds watching a progress bar,
 * give them a moment of arrival." So now Draft → Ready → (user clicks)
 * → Design.
 *
 * Content:
 *  - Big "Your site is live" headline
 *  - 1-sentence summary (DNA used, page count, elapsed)
 *  - Pages list with section counts
 *  - "Open editor" primary CTA (advances to Design)
 *  - "Preview as visitor" secondary (opens preview URL in new tab)
 *  - "Publish now" tertiary (skips Design, jumps to Publish)
 *
 * Auto-advances to Design after 12 seconds if untouched, so users who
 * step away aren't stuck on a celebration screen.
 */

import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Rocket, Eye, Edit3, CheckCircle2, Sparkles } from "lucide-react";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { STANDARD_S, EASE_QUIET } from "@/lib/motion";
import { getPlan, type PebblePlan } from "@/lib/state";
import { FirstBuildCelebration } from "@/components/first-build-celebration";
import { listProjects } from "@/lib/api";

type Props = {
  /** Build response — slug + preview_url + file_count. */
  build: {
    slug: string;
    preview_url: string;
    file_count?: number;
    [k: string]: unknown;
  } | null;
  /** Elapsed seconds for the build (if known). Shown as social-proof speed. */
  elapsedSeconds?: number;
  /** Continue → Design editor. */
  onOpenEditor: () => void;
  /** Skip ahead → Publish flow. */
  onPublish: () => void;
};

export function ReadyPhase({ build, elapsedSeconds, onOpenEditor, onPublish }: Props) {
  const [plan, setPlanLocal] = useState<PebblePlan | null>(null);
  const [autoAdvanceIn, setAutoAdvanceIn] = useState<number | null>(12);

  // 2026-05-24 funnel: post-build dopamine moment. Mounts once per
  // user (gated by both project count == 1 AND localStorage sentinel).
  // The highest-converting moment in any SaaS funnel.
  const [celebrating, setCelebrating] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (localStorage.getItem("pebble.first_build_celebrated") === "1") return;
    let cancelled = false;
    listProjects()
      .then((r) => {
        if (cancelled) return;
        if (r.projects && r.projects.length === 1) {
          setCelebrating(true);
          localStorage.setItem("pebble.first_build_celebrated", "1");
        }
      })
      .catch(() => { /* never block on this */ });
    return () => { cancelled = true; };
  }, []);

  // Load the cached plan so we can list pages + DNA + business name.
  // Falls back gracefully if the cache is empty (rare — plan is set during
  // /api/generate). Empty state still renders the headline + CTAs.
  useEffect(() => {
    setPlanLocal(getPlan());
  }, []);

  // Auto-advance to editor after 12s if the user doesn't click anything.
  // Counter ticks in 1s decrements; pauses on hover or keyboard focus so
  // someone scanning the page isn't yanked away.
  useEffect(() => {
    if (autoAdvanceIn === null) return;
    if (autoAdvanceIn <= 0) {
      onOpenEditor();
      return;
    }
    const t = setTimeout(() => setAutoAdvanceIn((n) => (n === null ? null : n - 1)), 1000);
    return () => clearTimeout(t);
  }, [autoAdvanceIn, onOpenEditor]);

  const cancelAutoAdvance = () => setAutoAdvanceIn(null);

  // Cancel auto-advance on ANY key press anywhere on the page.
  // <main onKeyDown> doesn't work because <main> isn't focusable — the
  // listener never fires. Attach to document instead so a stray keypress
  // (someone scanning the page) does what the user expects.
  useEffect(() => {
    if (autoAdvanceIn === null) return;
    const handler = () => setAutoAdvanceIn(null);
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [autoAdvanceIn]);

  const businessName = plan?.meta?.business_name || "your site";
  const dnaLabel = plan?.style?.label || null;
  const pages = plan?.pages || [];

  return (
    <main
      className="flex-1 overflow-y-auto flex flex-col items-center justify-center px-4 py-16"
      onMouseMove={cancelAutoAdvance}
    >
      {/* Celebration mark — slight scale-pop on mount. */}
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: STANDARD_S, ease: EASE_QUIET }}
        className="w-16 h-16 rounded-full bg-foreground text-background flex items-center justify-center mb-6"
      >
        <CheckCircle2 className="w-8 h-8" strokeWidth={2.5} />
      </motion.div>

      <motion.div
        initial="hidden"
        animate="visible"
        variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }}
        className="max-w-2xl w-full text-center space-y-8"
      >
        <motion.div
          variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
          className="space-y-3"
        >
          <h1 className={`${type.display.xl} text-foreground`}>{businessName} is live.</h1>
          <p className={`${type.body.m} text-muted-foreground`}>
            {pages.length > 0 && (
              <>
                {pages.length} {pages.length === 1 ? "page" : "pages"}
                {dnaLabel && <> · {dnaLabel}</>}
              </>
            )}
            {elapsedSeconds && pages.length > 0 && " · "}
            {elapsedSeconds && (
              <>Built in {elapsedSeconds < 60 ? `${elapsedSeconds}s` : `${Math.floor(elapsedSeconds / 60)}m ${elapsedSeconds % 60}s`}</>
            )}
          </p>
        </motion.div>

        {/* Pages list — what actually got shipped. Skim-scannable. */}
        {pages.length > 0 && (
          <motion.div
            variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
            className="bg-card border border-border rounded-2xl p-6 text-left"
          >
            <h2 className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground mb-3">
              Pages shipped
            </h2>
            <ul className="space-y-2">
              {pages.map((p) => (
                <li key={p.id} className="flex items-start justify-between gap-3 py-1">
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-foreground">{p.title}</p>
                    {p.purpose && (
                      <p className="text-xs text-muted-foreground line-clamp-1">{p.purpose}</p>
                    )}
                  </div>
                  <span className="font-mono text-[10px] text-muted-foreground/70 shrink-0 mt-1">
                    {p.route}
                  </span>
                </li>
              ))}
            </ul>
          </motion.div>
        )}

        {/* Primary action row */}
        <motion.div
          variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
          className="space-y-3"
        >
          <motion.button
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.97 }}
            onClick={onOpenEditor}
            className={`${interactions.button} w-full max-w-sm mx-auto bg-primary text-primary-foreground font-bold py-3.5 px-7 rounded-full shadow-lg flex items-center justify-center gap-2`}
          >
            <Edit3 className="w-4 h-4" />
            Open editor
          </motion.button>
          <div className="flex gap-3 justify-center flex-wrap pt-1">
            {build?.preview_url && (
              <a
                href={build.preview_url}
                target="_blank"
                rel="noopener"
                className={`${interactions.chip} flex items-center gap-2 bg-card border border-border text-foreground px-5 py-2.5 rounded-full font-semibold text-sm`}
              >
                <Eye className="w-3.5 h-3.5" /> Preview as visitor
              </a>
            )}
            <button
              onClick={onPublish}
              className={`${interactions.chip} flex items-center gap-2 bg-card border border-border text-foreground px-5 py-2.5 rounded-full font-semibold text-sm`}
            >
              <Rocket className="w-3.5 h-3.5" /> Publish now
            </button>
          </div>
        </motion.div>

        {/* Auto-advance countdown — quietly informs without nagging. */}
        {autoAdvanceIn !== null && autoAdvanceIn <= 8 && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.55 }}
            className="text-[11px] text-muted-foreground"
          >
            Opening editor in {autoAdvanceIn}s — move your mouse to stay here.
          </motion.p>
        )}

        <motion.p
          variants={{ hidden: { opacity: 0 }, visible: { opacity: 1 } }}
          className="text-xs text-muted-foreground/70 inline-flex items-center gap-1.5 justify-center"
        >
          <Sparkles className="w-3 h-3" />
          Everything is editable later. Nothing about this is final.
        </motion.p>
      </motion.div>

      <FirstBuildCelebration
        open={celebrating}
        onClose={() => setCelebrating(false)}
      />
    </main>
  );
}
