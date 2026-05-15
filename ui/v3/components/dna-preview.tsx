"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Shuffle } from "lucide-react";
import { getBrief, patchBrief } from "@/lib/state";

/**
 * Live DNA preview chip strip — sits at the top of the questionnaire so
 * the user can SEE their style direction emerging before generation.
 *
 * Why this is the differentiator: Lovable / Base44 ship template
 * galleries (pre-baked options the user picks). Pebble generates fresh
 * against a Style DNA, so we can show "your style is forming" in real
 * time. Template-gallery competitors structurally can't do this — there
 * is no "your style"; there's only the gallery.
 *
 * The strip:
 * - Shows the current DNA card label, a 3-swatch palette, and the
 *   display + body font names (the visual signal that the build will
 *   feel distinct).
 * - "Try another" rerolls — passes the seen-set as ?exclude= so the
 *   user always sees a different card.
 * - Persists the chosen DNA id into the brief via `_design_dna_id` so
 *   the engine's _select_dna picker honors it instead of rolling a new
 *   random one at /api/plan + /api/generate time.
 * - On mount, honors a `_inspire_dna_hint` already in the brief (set
 *   by /api/inspire on /migrate). Consumes the hint after use so a
 *   "Try another" reroll doesn't snap back to it.
 */

type DnaCard = {
  id: string;
  label: string;
  feel: string;
  display_font: string;
  body_font: string;
  mono_font?: string;
  palette_posture: string;
  hero_structure?: string;
  motion_intensity?: string;
  signature_moves?: string[];
  forbidden?: string[];
};

type DnaPreviewResponse = {
  ok: boolean;
  card: DnaCard;
  total: number;
  error?: string;
};

const HEX_RE = /#([0-9A-Fa-f]{6})\b/g;

function paletteSwatches(card: DnaCard): string[] {
  const matches = card.palette_posture.match(HEX_RE) ?? [];
  // Dedupe while preserving order, cap at 4.
  const seen = new Set<string>();
  const out: string[] = [];
  for (const raw of matches) {
    const norm = raw.toLowerCase();
    if (seen.has(norm)) continue;
    seen.add(norm);
    out.push(norm);
    if (out.length >= 4) break;
  }
  return out;
}

export function DnaPreview() {
  const [card, setCard] = useState<DnaCard | null>(null);
  const [seen, setSeen] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCard = useCallback(async (excludeIds: string[], idHint?: string) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (idHint) {
        params.set("id", idHint);
      } else if (excludeIds.length) {
        params.set("exclude", excludeIds.join(","));
      }
      const url = `/api/dna/preview${params.toString() ? `?${params}` : ""}`;
      const res = await fetch(url, { cache: "no-store" });
      const body: DnaPreviewResponse = await res.json();
      if (!res.ok || !body.ok) {
        // An inspire-supplied id we don't recognise (renamed/removed card) —
        // silently fall back to a random pick so the chip strip still renders.
        if (idHint && res.status === 404) {
          setLoading(false);
          void fetchCard(excludeIds);
          return;
        }
        setError(body.error || `unexpected ${res.status}`);
        return;
      }
      setCard(body.card);
      setSeen((prev) => {
        const next = new Set(prev);
        next.add(body.card.id);
        // If we've seen them all, reset so the user can keep rerolling.
        if (next.size >= body.total) next.clear();
        return next;
      });
      patchBrief({ _design_dna_id: body.card.id });
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(`couldn't reach the engine: ${msg}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // If /api/inspire pre-seeded the brief with a DNA suggestion, hydrate
    // to it on first paint so the user sees "yes, your taste matters."
    // Consume the hint immediately so a "Try another" reroll doesn't snap
    // back to the inspiration card — once shown, the user is steering.
    const brief = getBrief();
    const hint = (brief._inspire_dna_hint as string) || "";
    if (hint) {
      patchBrief({ _inspire_dna_hint: "" });
      void fetchCard([], hint);
    } else {
      void fetchCard([]);
    }
    // fetchCard is stable (useCallback with empty deps); intentional one-shot mount fetch.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onReroll = () => {
    if (loading) return;
    void fetchCard(Array.from(seen));
  };

  if (error && !card) {
    // Failsafe: render NOTHING if the engine isn't reachable. The
    // questionnaire still works — DNA preview is a delight, not a
    // dependency. (Engine logs the error; we don't surface a red banner
    // because that would confuse non-technical users.)
    return null;
  }

  return (
    <div className="px-4 md:px-8 pt-4">
      <div className="mx-auto max-w-3xl">
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex items-center gap-3 rounded-xl border border-border bg-card/60 px-4 py-3 backdrop-blur"
        >
          <Sparkles className="w-4 h-4 text-secondary flex-shrink-0" aria-hidden />
          <span className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground hidden sm:inline">
            Style direction
          </span>

          <AnimatePresence mode="wait">
            {card && (
              <motion.div
                key={card.id}
                initial={{ opacity: 0, x: 8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                transition={{ duration: 0.25 }}
                className="flex items-center gap-3 flex-1 min-w-0"
              >
                <span className="font-display text-sm md:text-base font-semibold text-foreground truncate">
                  {card.label}
                </span>

                <div className="flex items-center gap-1 flex-shrink-0" aria-label={`Palette: ${paletteSwatches(card).join(", ")}`}>
                  {paletteSwatches(card).map((hex) => (
                    <span
                      key={hex}
                      title={hex}
                      className="w-4 h-4 rounded-full border border-border/60"
                      style={{ backgroundColor: hex }}
                    />
                  ))}
                </div>

                <span className="text-xs text-muted-foreground hidden md:inline truncate">
                  {card.display_font} · {card.body_font}
                </span>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            type="button"
            onClick={onReroll}
            disabled={loading}
            className="ml-auto flex items-center gap-1.5 text-xs font-semibold text-muted-foreground hover:text-foreground px-2 py-1.5 rounded-md hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-wait flex-shrink-0"
            title="Try a different style direction"
          >
            <Shuffle className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden />
            <span className="hidden sm:inline">Try another</span>
          </button>
        </motion.div>
      </div>
    </div>
  );
}
