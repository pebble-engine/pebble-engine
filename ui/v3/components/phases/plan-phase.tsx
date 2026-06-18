"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Edit3, Sparkles, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { getBrief, getPlan, setPlan, patchBrief, type PebblePlan, type PebbleSetupItem } from "@/lib/state";
import { fetchPlan, fetchBriefCompose, generateSite, type GenerateResponse } from "@/lib/api";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC, EASE_QUIET, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import { formatProjectTitle } from "@/lib/brief-display";
import { PlanWireframeSkeleton } from "@/components/phases/plan-wireframe-skeleton";

/**
 * Plan phase — Phase 46b (2026-05-22) Base44-style restructure.
 *
 * Marc shared Base44's plan card showing a single elegant card with
 * five clearly-labelled sections (Intent & Goal / Audience & Roles /
 * Core Flows / Technical Requirements / Design Preferences) and a
 * "Start Building" button. He thought it was "executed appropriately"
 * — denser, more readable, less wizard-y than our previous 6-card
 * stack.
 *
 * This rewrite preserves all the underlying data (no info loss) but
 * lays it out as Base44 does:
 *   - One outer Plan card holds the five labelled sections
 *   - Each section is a label-row + body-content pair
 *   - A "Show less" toggle condenses very long sections
 *   - Launch Setup stays a separate card below (it's its own thing —
 *     dependency graph + auto/pending/manual badges don't compress
 *     well into a sentence)
 *   - Reroll-DNA + Edit + Generate buttons preserved
 *
 * Phase 40i — plan-first flow; reads brief.planFirst (set by
 * DetectiveInput) and inserts a /api/plan preview step before
 * /api/generate. When planFirst is true the back-button reads "Change
 * my mind" and returns to welcome; otherwise it reads "Edit the
 * questions" and returns to the idea phase.
 */

type Props = {
  onBack: () => void;
  onGenerate: (kickOff: () => Promise<GenerateResponse>) => void;
  /** Phase 40i: true when the user came via the plan-first shortcut from DetectiveInput. */
  planFirst?: boolean;
};

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function PlanPhase({ onBack, onGenerate, planFirst = false }: Props) {
  const [plan, setPlanLocal] = useState<PebblePlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [rerolling, setRerolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLess, setShowLess] = useState(() =>
    typeof window !== "undefined" && window.matchMedia("(max-width: 640px)").matches,
  );
  const [composing, setComposing] = useState(true);
  const startedRef = useRef(false);

  const safeCardVariants = useMemo(() => withReducedMotion(cardVariants), []);

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
    let cancelled = false;

    async function loadPlan() {
      const brief = getBrief();
      setComposing(true);
      try {
        const composed = await fetchBriefCompose({
          _raw_prompt: brief._raw_prompt || brief.extra_context,
          business_name: brief.business_name,
          business_type: brief.business_type,
          location: brief.location,
          audience: brief.audience,
          site_functions: brief.site_functions,
          brand_tone: brief.brand_tone,
          intent: brief.intent,
        });
        if (!cancelled && composed.ok && composed.brief_patch) {
          patchBrief(composed.brief_patch as Partial<typeof brief>);
        }
      } catch {
        /* hidden enrichment — plan still loads from visible fields */
      } finally {
        if (!cancelled) setComposing(false);
      }

      if (cancelled) return;

      const cached = getPlan();
      if (cached) {
        setPlanLocal(cached);
        return;
      }
      if (startedRef.current) return;
      startedRef.current = true;
      setLoading(true);
      try {
        const result = await fetchPlan(getBrief());
        if (cancelled) return;
        setPlan(result.plan);
        patchBrief({
          _industry_intel_key: result.industry_key || undefined,
          _design_dna_id: result.dna_id || undefined,
        });
        setPlanLocal(result.plan);
      } catch (e: unknown) {
        if (!cancelled) {
          const msg = e instanceof Error ? e.message : String(e);
          setError(msg);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    void loadPlan();
    return () => { cancelled = true; };
  }, []);

  const handleGenerate = () => {
    if (!plan || composing) return;
    onGenerate(() => generateSite(getBrief()));
  };

  if (loading && !error) {
    return <PlanWireframeSkeleton />;
  }

  if (!plan) {
    return (
      <div className="flex flex-col items-center justify-center px-4 py-20 text-center gap-6">
        {error ? (
          <p className="text-destructive">{error}</p>
        ) : (
          <Loader2 className="w-10 h-10 animate-spin text-foreground/50" />
        )}
      </div>
    );
  }

  // Pre-compute concise section content. Each section is a string OR a
  // ReactNode — strings get the "show less" length truncation; nodes pass
  // through as-is (lists, palette swatches, etc.).
  const intentAndGoal = plan.goal;
  const audienceAndRoles = plan.audience;
  const brief = getBrief();
  const projectTitle = formatProjectTitle({
    business_name: brief.business_name as string,
    business_type: brief.business_type as string,
    location: brief.location as string,
    _raw_prompt: (brief._raw_prompt as string) || (brief.extra_context as string),
  });

  return (
    <div className="px-4 md:px-8 py-8 max-w-3xl mx-auto w-full space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: STANDARD_S, ease: EASE_CINEMATIC }}
        className="space-y-2"
      >
        <h1 className={`${type.display.l} text-foreground`}>Plan</h1>
        <p className={`${type.readable.body} text-muted-foreground`}>
          Here&apos;s what I&apos;ll build for{" "}
          <span className="text-foreground font-semibold">{projectTitle.headline}</span>.
          Edit anything before generating.
        </p>
      </motion.div>

      {/* Main Plan card — Base44 layout: single elegant container, labelled
          sections separated by hairlines, optional show-less collapse. */}
      <motion.article
        variants={safeCardVariants}
        initial="hidden"
        animate="visible"
        transition={{ duration: STANDARD_S, ease: EASE_QUIET }}
        className="bg-card border border-border rounded-2xl shadow-[var(--shadow-1)] overflow-hidden"
      >
        <div className="p-6 md:p-8 space-y-6">
          <Section label="Your goal" condense={showLess} maxChars={180}>
            <p className={`${type.readable.body} text-foreground`}>{intentAndGoal}</p>
          </Section>

          <Section label="Who it's for" condense={showLess} maxChars={180}>
            <p className={`${type.readable.body} text-foreground`}>{audienceAndRoles}</p>
          </Section>

          <Section label="Pages we'll create" condense={showLess}>
            <ul className="space-y-2">
              {plan.pages.map((page) => (
                <li key={page.id} className={`flex items-start gap-2 ${type.readable.body}`}>
                  <span className="text-muted-foreground/60 font-mono mt-1 shrink-0">•</span>
                  <div className="min-w-0">
                    <span className="font-semibold text-foreground">{page.title}</span>
                    {!showLess && page.purpose && (
                      <span className="text-muted-foreground"> — {page.purpose}</span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </Section>

          <Section label="What's included" condense={showLess}>
            <div className="flex flex-wrap gap-2">
              {plan.features.map((f) => (
                <span
                  key={f.id}
                  className="px-3 py-2 min-h-10 bg-background border border-border rounded-full text-sm font-semibold text-foreground"
                >
                  {f.label}
                </span>
              ))}
            </div>
          </Section>

          <Section
            label="Look and feel"
            condense={showLess}
            rightSlot={
              <button
                type="button"
                onClick={handleRerollDna}
                disabled={rerolling}
                className={`${interactions.chip} inline-flex items-center gap-1 text-[11px] font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground disabled:opacity-50 disabled:cursor-wait`}
                title="Pick a different visual style for the same answers"
              >
                {rerolling ? (
                  <Loader2 className="w-3 h-3 animate-spin" aria-hidden />
                ) : (
                  <Sparkles className="w-3 h-3" aria-hidden />
                )}
                {rerolling ? "Picking" : "Reroll"}
              </button>
            }
          >
            <div className="space-y-3">
              <p className={`${type.heading.s} text-foreground`}>
                {plan.style.mood || plan.style.label}
              </p>
              {!showLess && (
                <>
                  <div className="flex items-center gap-3 flex-wrap">
                    {Object.entries(plan.style.palette || {}).map(([name, hex]) =>
                      hex ? (
                        <div
                          key={name}
                          className="flex items-center gap-1.5"
                          title={`${name}: ${hex}`}
                        >
                          <div
                            className="w-5 h-5 rounded-full border border-border shadow-sm"
                            style={{ backgroundColor: hex }}
                          />
                          <span className="text-[11px] font-mono text-muted-foreground">{hex}</span>
                        </div>
                      ) : null,
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    <span className="font-semibold text-foreground">{plan.style.fonts.display || "—"}</span>{" "}
                    + <span className="text-foreground">{plan.style.fonts.body || "—"}</span>
                  </p>
                </>
              )}
            </div>
          </Section>

          {plan.language && plan.language.code !== "en" && (
            <Section label="Language" condense={false}>
              <p className="text-sm text-foreground">
                Site copy in{" "}
                <span className="font-semibold">{plan.language.native_name}</span>{" "}
                <span className="text-muted-foreground">({plan.language.english_name})</span>.
              </p>
            </Section>
          )}
        </div>

        {/* Show less / Show more toggle — Base44 pattern. Sits at the bottom
            of the plan card. Defaults to expanded; one click compacts the
            long sections (Pages purposes, palette hexes, font names). */}
        <button
          type="button"
          onClick={() => setShowLess((v) => !v)}
          className={`w-full px-6 md:px-8 py-3.5 border-t border-border text-sm font-semibold text-muted-foreground hover:text-foreground hover:bg-muted/40 flex items-center justify-center gap-1.5 transition-colors min-h-11`}
        >
          {showLess ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          {showLess ? "Show more" : "Show less"}
        </button>
      </motion.article>

      {/* Launch Setup — separate card. The dependency graph + auto/pending/
          manual badges don't condense into a sentence; better as its own
          surface so users can scan what Pebble will and won't handle. */}
      <motion.article
        variants={safeCardVariants}
        initial="hidden"
        animate="visible"
        transition={{ duration: STANDARD_S, delay: 0.05, ease: EASE_QUIET }}
        className="bg-card border border-border rounded-2xl p-6 md:p-8 shadow-[var(--shadow-1)] space-y-4"
      >
        <div>
          <h3 className={`${type.heading.m} text-foreground`}>Launch Setup</h3>
          <p className="text-xs text-muted-foreground mt-1">
            {plan.setup_needs.length} items. Pebble handles what it can; the rest is honest about what&apos;s next.
          </p>
        </div>
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
                <div className="flex justify-between items-center gap-2">
                  <span className={type.label}>{item.label}</span>
                  <span
                    className={`text-xs font-bold uppercase tracking-wide px-2 py-1 rounded-full ${
                      item.status === "auto"
                        ? "bg-foreground/10 text-foreground"
                        : item.status === "pending"
                          ? "bg-foreground/15 text-foreground"
                          : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {item.status === "auto" ? "Auto" : item.status === "pending" ? "Soon" : "You"}
                  </span>
                </div>
                {blockingDeps.length > 0 && (
                  <p className="text-xs font-semibold text-muted-foreground leading-snug">
                    Unlocks after: {blockingDeps.map((d) => d.label).join(" + ")}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </motion.article>

      {/* Action row — Edit (back) + Start Building (primary). Base44's
          big-button-bottom-of-card pattern. */}
      <div className="pt-2 pb-safe flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={onBack}
          className={`${interactions.chip} flex items-center gap-2 text-muted-foreground hover:text-foreground px-3 py-2 rounded-md ${type.label}`}
        >
          <Edit3 className="w-3.5 h-3.5" />
          {planFirst ? "Change my mind" : "Edit the questions"}
        </button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleGenerate}
          disabled={composing || !plan}
          className={`${interactions.button} w-full sm:w-auto min-w-[260px] min-h-[52px] text-base bg-primary text-primary-foreground font-bold py-3.5 px-7 rounded-full shadow-lg flex items-center justify-center gap-2 disabled:opacity-50`}
        >
          <Sparkles className="w-4 h-4" /> {composing ? "Preparing…" : "Start Building"}
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

// ---------------------------------------------------------------------------
// Section — labeled section row inside the main Plan card.
// ---------------------------------------------------------------------------

function Section({
  label,
  children,
  condense,
  maxChars,
  rightSlot,
}: {
  label: string;
  children: React.ReactNode;
  /** When true, truncate string content past maxChars and hide non-essential bits. */
  condense?: boolean;
  /** Used only when the child is a single <p> string we can truncate. */
  maxChars?: number;
  /** Optional element to right-align next to the label (e.g. Reroll button). */
  rightSlot?: React.ReactNode;
}) {
  // For simple paragraph content, optionally truncate when condensed.
  let body = children;
  if (
    condense &&
    maxChars &&
    typeof children === "object" &&
    children !== null &&
    "props" in children &&
    typeof (children as { props?: { children?: unknown } }).props?.children === "string"
  ) {
    const text = (children as { props: { children: string } }).props.children;
    if (text.length > maxChars) {
      body = <p className="leading-relaxed text-foreground">{text.slice(0, maxChars).trimEnd()}…</p>;
    }
  }
  return (
    <div className="border-b border-border last:border-0 pb-6 last:pb-0">
      <div className="flex items-center justify-between gap-3 mb-2">
        <h3 className={`${type.readable.label} mb-2`}>
          {label}
        </h3>
        {rightSlot}
      </div>
      {body}
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
