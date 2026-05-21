"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Edit3, Sparkles, Loader2 } from "lucide-react";
import { getBrief, getPlan, setPlan, patchBrief, type PebblePlan, type PebbleSetupItem } from "@/lib/state";
import { fetchPlan, generateSite, type GenerateResponse } from "@/lib/api";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC, EASE_QUIET, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

/**
 * Plan phase — the user-facing "here's what I'll build" review screen.
 *
 * On mount, calls /api/plan if no plan is cached yet (i.e. user just
 * came from the idea phase) and shows a skeleton state while it loads.
 * Once the plan is in memory, displays the seven sections (audience,
 * goal, pages, features, style, setup, language) and a big Generate
 * button.
 *
 * Generate kicks off the full LLM build via /api/generate. The phase
 * shell handles the transition: when Generate is clicked, the shell
 * jumps to draft phase, awaits the response, and jumps to design phase
 * when complete.
 */

type Props = {
  onBack: () => void;
  onGenerate: (kickOff: () => Promise<GenerateResponse>) => void;
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function Card({ children, delay = 0, className = "" }: { children: React.ReactNode; delay?: number; className?: string }) {
  const safeCardVariants = useMemo(() => withReducedMotion(cardVariants), []);
  return (
    <motion.article
      variants={safeCardVariants}
      initial="hidden"
      animate="visible"
      transition={{ duration: STANDARD_S, delay, ease: EASE_QUIET }}
      className={`bg-card border border-border rounded-2xl p-6 md:p-8 shadow-[var(--shadow-1)] ${className}`}
    >
      {children}
    </motion.article>
  );
}

export function PlanPhase({ onBack, onGenerate }: Props) {
  const [plan, setPlanLocal] = useState<PebblePlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [rerolling, setRerolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const startedRef = useRef(false);

  /**
   * Phase 15b — re-pick Layout DNA + Style DNA for the same brief.
   * Clears the pinned IDs so the engine's pickers re-roll, then refetches
   * the plan. Lets the user iterate on the look without restarting the
   * questionnaire from scratch.
   */
  const handleRerollDna = async () => {
    if (rerolling) return;
    setRerolling(true);
    setError(null);
    // Clear the pinned DNA ids so the picker re-rolls
    patchBrief({ _design_dna_id: undefined, _layout_dna_id: undefined });
    try {
      const result = await fetchPlan(getBrief());
      setPlan(result.plan);
      patchBrief({
        _industry_intel_key: result.industry_key || undefined,
        _design_dna_id: result.dna_id || undefined,
      });
      setPlanLocal(result.plan);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(`reroll failed: ${msg}`);
    } finally {
      setRerolling(false);
    }
  };

  useEffect(() => {
    // Use cached plan when present. Otherwise compute it fresh — usually
    // means we just arrived from the idea phase.
    const cached = getPlan();
    if (cached) {
      setPlanLocal(cached);
      return;
    }
    if (startedRef.current) return;
    startedRef.current = true;
    setLoading(true);
    fetchPlan(getBrief())
      .then((result) => {
        setPlan(result.plan);
        patchBrief({
          _industry_intel_key: result.industry_key || undefined,
          _design_dna_id: result.dna_id || undefined,
        });
        setPlanLocal(result.plan);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleGenerate = () => {
    if (!plan) return;
    onGenerate(() => generateSite(getBrief()));
  };

  if (loading && !error) {
    return (
      <div className="w-full max-w-2xl mx-auto space-y-4 animate-pulse px-4 py-8">
        {/* Header skeleton */}
        <div className="text-center mb-6 space-y-2">
          <div className="h-8 bg-muted rounded-lg w-48 mx-auto" />
          <div className="h-4 bg-muted rounded w-72 mx-auto" />
        </div>
        {/* Card skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-2xl border border-border bg-card p-6 space-y-3">
              <div className="h-4 bg-muted rounded w-24" />
              <div className="h-6 bg-muted rounded w-40" />
              <div className="h-3 bg-muted rounded w-full" />
              <div className="h-3 bg-muted rounded w-3/4" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="flex flex-col items-center justify-center px-4 py-20 text-center gap-6">
        {error ? (
          <p className="text-destructive">{error}</p>
        ) : (
          <Loader2 className="w-10 h-10 animate-spin text-secondary" />
        )}
      </div>
    );
  }

  return (
    <div className="px-4 md:px-8 py-8 max-w-3xl mx-auto w-full space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="text-center space-y-2"
      >
        <h1 className={`${type.display.l} text-primary`}>The Pebble Plan</h1>
        <p className={`${type.body.m} text-muted-foreground`}>
          Verify what I&apos;ll build before I generate the first draft.
        </p>
      </motion.div>

      <Card delay={0.05}>
        <div className="flex justify-between items-start mb-3">
          <h3 className={`${type.heading.m} text-primary`}>Who I think this is for</h3>
          <span className="px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider text-muted-foreground bg-accent">
            Audience
          </span>
        </div>
        <p className="leading-relaxed text-foreground">{plan.audience}</p>
      </Card>

      <Card delay={0.1}>
        <h3 className={`${type.heading.m} text-primary mb-2`}>The one thing I&apos;m optimizing for</h3>
        <p className="leading-relaxed text-foreground">{plan.goal}</p>
      </Card>

      <Card delay={0.15}>
        <h3 className={`${type.heading.m} text-primary mb-4`}>Pages I&apos;ll create</h3>
        <div className="space-y-2">
          {plan.pages.map((page) => (
            <div
              key={page.id}
              className="flex justify-between items-start py-2 border-b border-border last:border-0"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className={`${type.label} text-foreground`}>{page.title}</span>
                  <span
                    className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      page.foundation
                        ? "bg-secondary/20 text-secondary"
                        : "bg-spark/15 text-spark-deep"
                    }`}
                  >
                    {page.foundation ? "Foundation" : "Industry"}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">{page.purpose}</p>
              </div>
              <span className="text-[11px] font-bold uppercase tracking-wider font-mono text-muted-foreground/60 flex-shrink-0 ml-3">{page.route}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card delay={0.2}>
        <h3 className={`${type.heading.m} text-primary mb-3`}>Core capabilities</h3>
        <div className="flex flex-wrap gap-2">
          {plan.features.map((f) => (
            <span
              key={f.id}
              className={`px-3 py-2 bg-background border border-border rounded-full ${type.label}`}
            >
              {f.label}
            </span>
          ))}
        </div>
      </Card>

      <Card delay={0.25} className="overflow-hidden p-0">
        <div className="p-6 md:p-8 border-b border-border flex items-start justify-between gap-4">
          <div>
            <h3 className={`${type.heading.m} text-primary`}>Visual style</h3>
            <p className="text-xs text-muted-foreground italic mt-1">Inspired by {plan.style.label}</p>
          </div>
          {/* Phase 15b: reroll button — lets the user try a different
              DNA without restarting the questionnaire. Free (no LLM call;
              just re-runs the picker + plan computation). */}
          <button
            type="button"
            onClick={handleRerollDna}
            disabled={rerolling}
            className={`${interactions.chip} flex-shrink-0 inline-flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-md text-muted-foreground hover:text-foreground border border-border hover:border-foreground/40 disabled:opacity-50 disabled:cursor-wait`}
            title="Pick a different visual style for the same answers"
          >
            {rerolling ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin mr-1.5" aria-hidden />
            ) : (
              <Sparkles className="w-3.5 h-3.5" aria-hidden />
            )}
            <span className={type.label}>{rerolling ? "Picking…" : "Try a different style"}</span>
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2">
          <div className="p-6 md:p-8 bg-background">
            <p className={`${type.display.m} text-foreground`}>{plan.style.mood || plan.style.label}</p>
            <p className="font-mono text-[11px] font-bold uppercase tracking-wider text-muted-foreground mt-2">DNA-driven layout</p>
          </div>
          <div className="p-6 md:p-8 border-t md:border-t-0 md:border-l border-border space-y-4">
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Palette</p>
              <div className="flex gap-2">
                {Object.entries(plan.style.palette || {}).map(([name, hex]) =>
                  hex ? (
                    <div
                      key={name}
                      className="w-10 h-10 rounded-full border border-border shadow-sm"
                      style={{ backgroundColor: hex }}
                      title={`${name}: ${hex}`}
                    />
                  ) : null,
                )}
              </div>
            </div>
            <div>
              <p className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground mb-2">Typography</p>
              <p className={`${type.heading.s} text-primary`}>{plan.style.fonts.display || "—"}</p>
              <p className={`${type.body.s} text-foreground`}>{plan.style.fonts.body || "—"}</p>
            </div>
          </div>
        </div>
      </Card>

      {plan.language && plan.language.code !== "en" && (
        <Card delay={0.27}>
          <h3 className={`${type.heading.m} text-primary mb-2`}>Language</h3>
          <p className="leading-relaxed text-foreground">
            Site copy will be in{" "}
            <span className="font-semibold">{plan.language.native_name}</span>{" "}
            <span className="text-muted-foreground text-sm">({plan.language.english_name})</span>.
          </p>
        </Card>
      )}

      <Card delay={0.3}>
        <h3 className={`${type.heading.m} text-primary mb-1`}>Launch setup</h3>
        <p className="text-xs text-muted-foreground mb-3">
          {plan.setup_needs.length} items. Pebble handles what it can; the rest is honest about what&apos;s next.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {topoSortSetupNeeds(plan.setup_needs).map((item) => {
            const byId = new Map(plan.setup_needs.map((s) => [s.id, s]));
            const blockingDeps = item.dependencies
              .map((id) => byId.get(id))
              .filter((d): d is PebbleSetupItem => !!d && d.status !== "auto");
            return (
              <div
                key={item.id}
                className={`flex flex-col gap-1 p-3 rounded-lg border ${
                  item.status === "auto"
                    ? "bg-background/60 border-border/60 opacity-80"
                    : "bg-background border-border"
                }`}
                title={item.notes}
              >
                <div className="flex justify-between items-center">
                  <span className={type.label}>{item.label}</span>
                  <span
                    className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                      item.status === "auto"
                        ? "bg-earth/20 text-earth-deep"
                        : item.status === "pending"
                          ? "bg-spark/15 text-spark-deep"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {item.status === "auto" ? "Auto" : item.status === "pending" ? "Soon" : "You"}
                  </span>
                </div>
                {blockingDeps.length > 0 && (
                  <p className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground leading-tight">
                    Unlocks after: {blockingDeps.map((d) => d.label).join(" + ")}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={onBack}
          className={`${interactions.chip} flex items-center gap-2 text-muted-foreground hover:text-foreground px-3 py-2 rounded-md ${type.label}`}
        >
          <Edit3 className="w-3.5 h-3.5" /> Edit the questions
        </button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleGenerate}
          className={`${interactions.button} w-full sm:w-auto min-w-[260px] bg-primary text-primary-foreground font-semibold py-3.5 px-7 rounded-full shadow-lg flex items-center justify-center gap-2`}
        >
          <Sparkles className="w-4 h-4" /> Generate my draft
        </motion.button>
      </div>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
            className="p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/**
 * Topological sort of setup_needs so that dependencies render before
 * dependents — the chain is readable top-down. Stable for unrelated
 * items (preserves insertion order). Tolerates cycles by falling back
 * to insertion order; the python-side
 * `test_dependency_graph_has_no_cycles` is the real guard.
 */
function topoSortSetupNeeds(items: PebbleSetupItem[]): PebbleSetupItem[] {
  const byId = new Map(items.map((i) => [i.id, i]));
  const visited = new Set<string>();
  const out: PebbleSetupItem[] = [];

  function visit(id: string, stack: Set<string>) {
    if (visited.has(id) || stack.has(id)) return;
    const item = byId.get(id);
    if (!item) return;
    stack.add(id);
    for (const dep of item.dependencies) visit(dep, stack);
    stack.delete(id);
    visited.add(id);
    out.push(item);
  }

  for (const item of items) visit(item.id, new Set());
  return out;
}
