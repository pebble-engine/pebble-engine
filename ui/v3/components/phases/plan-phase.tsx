"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Edit3, Sparkles, Loader2 } from "lucide-react";
import { getBrief, getPlan, setPlan, patchBrief, type PebblePlan } from "@/lib/state";
import { fetchPlan, generateSite, type GenerateResponse } from "@/lib/api";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC, EASE_QUIET, withReducedMotion } from "@/lib/motion";

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
  const [error, setError] = useState<string | null>(null);
  const startedRef = useRef(false);

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

  if (loading || !plan) {
    return (
      <div className="flex flex-col items-center justify-center px-4 py-20 text-center gap-6">
        <Loader2 className="w-10 h-10 animate-spin text-secondary" />
        <p className="text-muted-foreground">
          {error ? (
            <span className="text-destructive">{error}</span>
          ) : (
            "Drafting the plan — pulling industry intel, picking a style, sketching pages…"
          )}
        </p>
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
        <h1 className="font-display text-3xl md:text-4xl font-bold text-primary">The Pebble Plan</h1>
        <p className="text-muted-foreground text-sm md:text-base">
          Verify what I&apos;ll build before I generate the first draft.
        </p>
      </motion.div>

      <Card delay={0.05}>
        <div className="flex justify-between items-start mb-3">
          <h3 className="font-display text-xl font-semibold text-primary">Who I think this is for</h3>
          <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-wider text-muted-foreground bg-accent">
            Audience
          </span>
        </div>
        <p className="leading-relaxed text-foreground">{plan.audience}</p>
      </Card>

      <Card delay={0.1}>
        <h3 className="font-display text-xl font-semibold text-primary mb-2">The one thing I&apos;m optimizing for</h3>
        <p className="leading-relaxed text-foreground">{plan.goal}</p>
      </Card>

      <Card delay={0.15}>
        <h3 className="font-display text-xl font-semibold text-primary mb-4">Pages I&apos;ll create</h3>
        <div className="space-y-2">
          {plan.pages.map((page) => (
            <div
              key={page.id}
              className="flex justify-between items-start py-2 border-b border-border last:border-0"
            >
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-foreground text-sm">{page.title}</span>
                  <span
                    className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                      page.foundation
                        ? "bg-secondary/20 text-secondary"
                        : "bg-spark/15 text-spark"
                    }`}
                  >
                    {page.foundation ? "Foundation" : "Industry"}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-0.5">{page.purpose}</p>
              </div>
              <span className="text-[10px] font-mono text-muted-foreground/60 flex-shrink-0 ml-3">{page.route}</span>
            </div>
          ))}
        </div>
      </Card>

      <Card delay={0.2}>
        <h3 className="font-display text-xl font-semibold text-primary mb-3">Core capabilities</h3>
        <div className="flex flex-wrap gap-2">
          {plan.features.map((f) => (
            <span
              key={f.id}
              className="px-3 py-1.5 bg-background border border-border rounded-full text-sm font-medium"
            >
              {f.label}
            </span>
          ))}
        </div>
      </Card>

      <Card delay={0.25} className="overflow-hidden p-0">
        <div className="p-6 md:p-8 border-b border-border">
          <h3 className="font-display text-xl font-semibold text-primary">Visual style</h3>
          <p className="text-xs text-muted-foreground italic mt-1">Inspired by {plan.style.label}</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2">
          <div className="p-6 md:p-8 bg-background">
            <p className="font-display text-2xl text-foreground leading-tight">{plan.style.mood || plan.style.label}</p>
            <p className="font-mono text-[10px] text-muted-foreground mt-2">DNA-driven layout</p>
          </div>
          <div className="p-6 md:p-8 border-t md:border-t-0 md:border-l border-border space-y-4">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">Palette</p>
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
              <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-2">Typography</p>
              <p className="font-display text-lg text-primary">{plan.style.fonts.display || "—"}</p>
              <p className="text-sm text-foreground">{plan.style.fonts.body || "—"}</p>
            </div>
          </div>
        </div>
      </Card>

      {plan.language && plan.language.code !== "en" && (
        <Card delay={0.27}>
          <h3 className="font-display text-xl font-semibold text-primary mb-2">Language</h3>
          <p className="leading-relaxed text-foreground">
            Site copy will be in{" "}
            <span className="font-semibold">{plan.language.native_name}</span>{" "}
            <span className="text-muted-foreground text-sm">({plan.language.english_name})</span>.
          </p>
        </Card>
      )}

      <Card delay={0.3}>
        <h3 className="font-display text-xl font-semibold text-primary mb-1">Launch setup</h3>
        <p className="text-xs text-muted-foreground mb-3">
          {plan.setup_needs.length} items. Pebble handles what it can; the rest is honest about what&apos;s next.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {plan.setup_needs.map((item) => (
            <div
              key={item.id}
              className="flex justify-between items-center p-2.5 bg-background rounded-lg border border-border"
              title={item.notes}
            >
              <span className="text-sm font-medium">{item.label}</span>
              <span
                className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase ${
                  item.status === "auto"
                    ? "bg-earth/20 text-earth"
                    : item.status === "pending"
                      ? "bg-spark/15 text-spark"
                      : "bg-muted text-muted-foreground"
                }`}
              >
                {item.status === "auto" ? "Auto" : item.status === "pending" ? "Soon" : "You"}
              </span>
            </div>
          ))}
        </div>
      </Card>

      <div className="pt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors px-3 py-2 rounded-md hover:bg-accent text-sm font-semibold"
        >
          <Edit3 className="w-3.5 h-3.5" /> Edit the questions
        </button>
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={handleGenerate}
          className="w-full sm:w-auto min-w-[260px] bg-primary text-primary-foreground font-semibold py-3.5 px-7 rounded-full shadow-lg hover:translate-y-[-2px] active:translate-y-0 transition-all flex items-center justify-center gap-2"
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
