"use client";

/**
 * TemplateMatchModal — shown right after signup completes, before
 * the user lands on the workspace. Surfaces the 3 best-matched
 * templates for their prompt so the first interaction is "pick one"
 * instead of "stare at a blank workspace."
 *
 * Three actions:
 *   1. "Use this one (1 credit)" → instantiateTemplate → router.push(/workspace/<slug>)
 *   2. "See all templates" → router.push("/templates")
 *   3. "Build from scratch (10 credits)" → disabled for free users
 *      (TierBadge hints Starter); paid users it closes the modal so the
 *      shell triggers the existing full-build flow.
 *
 * Mounted from the workspace shell when sessionStorage has
 * `pebble.first_signup_prompt`. The key is cleared by the shell on mount
 * so a re-render doesn't re-open the modal.
 */

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X } from "lucide-react";
import {
  matchTemplates,
  listTemplates,
  instantiateTemplate,
  type TemplateMatch,
  type TemplateSummary,
} from "@/lib/api";
import { TierBadge } from "@/components/tier-badge";
import { getBrief } from "@/lib/state";
import type { Brief } from "@/lib/state";
import type { PlanTier } from "@/lib/plan-features";

export type TemplateMatchModalProps = {
  open:    boolean;
  prompt:  string;
  plan:    PlanTier;
  onClose: () => void;
  onUsed:  (slug: string) => void;
};

type EnrichedMatch = TemplateMatch & { details: TemplateSummary };

export function TemplateMatchModal({
  open,
  prompt,
  plan,
  onClose,
  onUsed,
}: TemplateMatchModalProps) {
  const router = useRouter();
  const [matches, setMatches] = useState<EnrichedMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [instantiating, setInstantiating] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!open) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    void (async () => {
      try {
        const brief = getBrief();
        const [m, all] = await Promise.all([
          matchTemplates(prompt, (brief.business_type as string) || undefined, 3),
          listTemplates(),
        ]);
        if (cancelled) return;
        const enriched: EnrichedMatch[] = m.matches
          .map((match) => {
            const details = all.templates.find((t) => t.id === match.template_id);
            return details ? { ...match, details } : null;
          })
          .filter((x): x is EnrichedMatch => x !== null);
        setMatches(enriched);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Couldn't load template matches.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [open, prompt]);

  async function handleUse(templateId: string) {
    setInstantiating(templateId);
    setError(null);
    try {
      const brief = getBrief();
      const result = await instantiateTemplate(templateId, brief as Brief);
      onUsed(result.slug);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Couldn't build from this template.");
      setInstantiating(null);
    }
  }

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-3xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden p-7"
          >
            <button
              type="button"
              onClick={onClose}
              className="absolute top-3 right-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] uppercase tracking-widest font-bold">
                <Sparkles className="w-3 h-3" /> Matched for you
              </div>
              <h2 className="text-2xl md:text-3xl font-extrabold text-foreground mt-3 tracking-tight">
                Three templates for your business
              </h2>
              <p className="text-sm text-muted-foreground mt-2 max-w-md mx-auto">
                Start with one of these. You can customize colors, copy, photos — all without spending credits.
              </p>
            </div>

            {error && (
              <div role="alert" className="mb-4 px-3 py-2 rounded-md bg-destructive/10 text-destructive text-xs">
                {error}
              </div>
            )}

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[0, 1, 2].map((i) => (
                  <div key={i} className="aspect-[4/3] bg-muted/50 rounded-xl animate-pulse" />
                ))}
              </div>
            ) : matches.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-sm text-muted-foreground mb-4">No exact matches — browse the full gallery instead.</p>
                <button
                  type="button"
                  onClick={() => { onClose(); router.push("/templates"); }}
                  className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-bold"
                >
                  See all templates
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {matches.map((m) => (
                  <div key={m.template_id} className="bg-background border border-border rounded-xl overflow-hidden flex flex-col">
                    <div className="aspect-[4/3] bg-muted/50 relative overflow-hidden">
                      {m.details.preview_image && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={m.details.preview_image} alt={m.details.name} className="w-full h-full object-cover" />
                      )}
                    </div>
                    <div className="p-3 flex-1 flex flex-col">
                      <p className="text-sm font-bold text-foreground">{m.details.name}</p>
                      <p className="text-[11px] text-muted-foreground mt-0.5">{m.details.tagline}</p>
                      <button
                        type="button"
                        onClick={() => handleUse(m.template_id)}
                        disabled={instantiating !== null}
                        className="mt-auto w-full mt-3 px-3 py-2 rounded-full bg-primary text-primary-foreground text-xs font-bold disabled:opacity-50"
                      >
                        {instantiating === m.template_id ? "Building…" : "Use this one (1 credit)"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-6 flex items-center justify-center gap-4 text-xs">
              <button
                type="button"
                onClick={() => { onClose(); router.push("/templates"); }}
                className="text-primary font-bold hover:underline"
              >
                See all templates
              </button>
              <span className="text-muted-foreground">·</span>
              <button
                type="button"
                disabled={plan === "free"}
                onClick={onClose}
                className="text-muted-foreground disabled:cursor-not-allowed hover:text-foreground disabled:hover:text-muted-foreground inline-flex items-center gap-1.5"
              >
                Build from scratch (10 credits)
                {plan === "free" && <TierBadge tier="starter" />}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
