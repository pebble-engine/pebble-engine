"use client";

/**
 * BuildIntegrityChecklist — Phase 36 (2026-05-21).
 *
 * The Phase-4 diagram's "Build Integrity" panel: a curated 10-item
 * pre-launch checklist that animates pending → green check as each
 * eval completes. Builds user confidence in the moments before publish.
 *
 * UX model:
 *   - On mount (or when `slug` changes), fire /api/projects/<slug>/integrity.
 *   - While in flight: render every row in "pending" state with a spinner.
 *   - On response: rows animate to their final status — passing in sequence
 *     for cinematic effect rather than all at once.
 *   - Soft failures (status=fail, must_pass=false) render as amber warnings.
 *   - Hard failures (status=fail, must_pass=true) render as red blockers and
 *     the parent should disable the Publish button.
 *
 * The component takes no opinion on what to do with the publishable flag —
 * the parent screen decides whether to gate Publish or just inform.
 */
import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence, MotionConfig } from "framer-motion";
import { Check, X, AlertTriangle, MinusCircle } from "lucide-react";
import {
  checkBuildIntegrity,
  type IntegrityCheckRow,
  type IntegrityResponse,
} from "@/lib/api";
import { type } from "@/lib/type";

/** ms between revealing each row after the response lands. */
const REVEAL_STAGGER = 180;

type RowState =
  | { phase: "pending" }
  | { phase: "revealed"; row: IntegrityCheckRow };

function StatusGlyph({ row, pending }: { row: IntegrityCheckRow | null; pending: boolean }) {
  if (pending || row === null) {
    // Spinning ring — same vocabulary as the URL-extraction overlay.
    return (
      <motion.div
        aria-hidden
        className="w-4 h-4 rounded-full border-2 border-white/20 border-t-foreground/70"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
    );
  }
  if (row.status === "pass") {
    return <Check className="w-4 h-4 text-green-400" aria-label="passed" />;
  }
  if (row.status === "fail") {
    return row.must_pass
      ? <X            className="w-4 h-4 text-red-400"   aria-label="failed (must pass)" />
      : <AlertTriangle className="w-4 h-4 text-amber-400" aria-label="warning" />;
  }
  if (row.status === "skip") {
    return <MinusCircle className="w-4 h-4 text-muted-foreground/60" aria-label="skipped" />;
  }
  // error
  return <X className="w-4 h-4 text-red-400" aria-label="check errored" />;
}

function statusLabel(row: IntegrityCheckRow): string {
  if (row.status === "pass") return "Ready";
  if (row.status === "fail") return row.must_pass ? "Needs fix" : "Warning";
  if (row.status === "skip") return "Skipped";
  return "Errored";
}

function statusColor(row: IntegrityCheckRow): string {
  if (row.status === "pass") return "text-foreground";
  if (row.status === "fail") return row.must_pass ? "text-red-400" : "text-amber-300";
  if (row.status === "skip") return "text-muted-foreground/60";
  return "text-red-400";
}

export function BuildIntegrityChecklist({
  slug,
  onResult,
  className = "",
}: {
  slug: string;
  /** Fired once after the integrity call lands, so the parent can
      enable/disable the Publish button based on `publishable`. */
  onResult?: (res: IntegrityResponse) => void;
  className?: string;
}) {
  const [data, setData] = useState<IntegrityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [revealedIdx, setRevealedIdx] = useState(0);
  const fetchedSlugRef = useRef<string | null>(null);

  // Fetch once per slug. Don't refetch unless slug changes.
  useEffect(() => {
    if (fetchedSlugRef.current === slug) return;
    fetchedSlugRef.current = slug;
    setData(null);
    setError(null);
    setRevealedIdx(0);
    checkBuildIntegrity(slug)
      .then((res) => {
        setData(res);
        onResult?.(res);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : "Couldn't run integrity checks.");
      });
  }, [slug, onResult]);

  // Cinematic stagger: once the data lands, reveal rows one-by-one.
  useEffect(() => {
    if (!data) return;
    if (revealedIdx >= data.results.length) return;
    const id = window.setTimeout(() => {
      setRevealedIdx((i) => Math.min(i + 1, data.results.length));
    }, REVEAL_STAGGER);
    return () => window.clearTimeout(id);
  }, [data, revealedIdx]);

  // Decide what rows to render. Before data lands, show placeholders of
  // unknown length (10 dim pending rows is the canonical count).
  const placeholderCount = 10;
  const rowStates: RowState[] = data
    ? data.results.map((row, i) => i < revealedIdx
        ? { phase: "revealed" as const, row }
        : { phase: "pending" as const })
    : Array.from({ length: placeholderCount }, () => ({ phase: "pending" as const }));

  return (
    <MotionConfig reducedMotion="user">
      <div
        className={`rounded-xl border border-border bg-card/60 p-5 space-y-4 ${className}`}
        role="status"
        aria-live="polite"
      >
        <div className="flex items-baseline justify-between">
          <h3 className={type.heading.s}>Build integrity</h3>
          {data && (
            <span className={`${type.caption} ${data.publishable ? "text-green-400" : "text-amber-300"}`}>
              {data.passed} / {data.total} checks passed
              {data.publishable ? " — ready to publish" : ""}
            </span>
          )}
        </div>

        {error && (
          <div className="flex items-start gap-2 text-sm text-red-400 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
            <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" aria-hidden />
            <span>{error}</span>
          </div>
        )}

        <ul className="space-y-2.5">
          <AnimatePresence initial={false}>
            {rowStates.map((state, i) => {
              const isRevealed = state.phase === "revealed";
              const row = isRevealed ? state.row : null;
              const key = isRevealed ? row!.id : `placeholder-${i}`;

              return (
                <motion.li
                  key={key}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: isRevealed ? 1 : 0.45, x: 0 }}
                  transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                  className="flex items-center justify-between gap-3"
                >
                  <span className="flex items-center gap-3 min-w-0">
                    <StatusGlyph row={row} pending={!isRevealed} />
                    <span className={`text-sm ${isRevealed && row ? statusColor(row) : "text-muted-foreground/50"} truncate`}>
                      {isRevealed && row ? row.label : "Checking…"}
                    </span>
                  </span>
                  {isRevealed && row && (
                    <span className={`${type.caption} ${statusColor(row)} shrink-0`}>
                      {statusLabel(row)}
                    </span>
                  )}
                </motion.li>
              );
            })}
          </AnimatePresence>
        </ul>

        {data && !data.publishable && (
          <p className="text-xs text-muted-foreground pt-2 border-t border-border/40">
            Fix the items marked <strong className="text-red-400">Needs fix</strong> before publishing,
            or override and ship anyway from the publish dialog.
          </p>
        )}
      </div>
    </MotionConfig>
  );
}
