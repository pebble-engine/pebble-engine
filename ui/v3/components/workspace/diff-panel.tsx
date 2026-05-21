"use client";

/**
 * DiffPanel — Phase 35 (2026-05-21).
 *
 * Renders the post-mutation diff returned by /api/refine + /api/visual-edit.
 * The Phase-3 diagram pattern: after every change, show the user exactly
 * what touched, broken into categories so the AI feels like a colleague
 * who shows their work — not a magic box.
 *
 * Two density modes:
 *   - compact: one-line summary, "Updated 3 files (Frontend, Config)"
 *              Used inline in a chat-thread message.
 *   - expanded: category roll-up + per-file list with line counts.
 *               Used when the user clicks into the message to see detail.
 *
 * Untouched categories ("Backend: Untouched") are surfaced explicitly when
 * the consumer passes `showUntouched` — this is the diagram's "Setup API:
 * Untouched" reassurance pattern. Defaults off; the compact mode never
 * shows untouched.
 */
import { type DiffSummary, type FileDiff } from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Check, Plus, Minus, Pencil, ChevronDown } from "lucide-react";
import { useState } from "react";
import { type } from "@/lib/type";

const ALL_CATEGORIES = ["Frontend", "Backend", "Styles", "Assets", "Config", "Tests", "Other"] as const;
type Category = typeof ALL_CATEGORIES[number];

function StatusIcon({ status }: { status: FileDiff["status"] }) {
  if (status === "added")    return <Plus  className="w-3.5 h-3.5 text-green-400" aria-label="added" />;
  if (status === "deleted")  return <Minus className="w-3.5 h-3.5 text-red-400"   aria-label="deleted" />;
  return <Pencil className="w-3.5 h-3.5 text-blue-400" aria-label="modified" />;
}

function LineDelta({ added, removed }: { added: number | null; removed: number | null }) {
  if (added == null && removed == null) {
    return <span className="text-xs text-muted-foreground/60">binary</span>;
  }
  const parts: string[] = [];
  if (added) parts.push(`+${added}`);
  if (removed) parts.push(`-${removed}`);
  if (parts.length === 0) parts.push("0");
  return <span className="text-xs font-mono text-muted-foreground/70 tabular-nums">{parts.join(" ")}</span>;
}

function CategoryRow({ name, count, total }: { name: string; count: number; total: number }) {
  // No-op rows ("Backend: Untouched") render dimmer.
  const touched = count > 0;
  return (
    <div className="flex items-baseline justify-between py-1.5">
      <span className={`${type.eyebrow} ${touched ? "text-foreground" : "text-muted-foreground/50"}`}>
        {name}
      </span>
      <span className={`text-sm ${touched ? "text-foreground" : "text-muted-foreground/50"}`}>
        {touched
          ? <>{count} file{count === 1 ? "" : "s"} ({Math.round((count / total) * 100)}%)</>
          : "Untouched"}
      </span>
    </div>
  );
}

export function DiffPanel({
  diff,
  mode = "expanded",
  showUntouched = false,
  className = "",
}: {
  diff: DiffSummary | null;
  mode?: "compact" | "expanded";
  /** When true, render every category in ALL_CATEGORIES, marking unaffected ones "Untouched". */
  showUntouched?: boolean;
  className?: string;
}) {
  const [filesOpen, setFilesOpen] = useState(false);

  if (!diff || diff.total_changed === 0) {
    return (
      <div className={`flex items-center gap-2 text-sm text-muted-foreground ${className}`}>
        <Check className="w-4 h-4 text-green-400" aria-hidden />
        <span>No files changed.</span>
      </div>
    );
  }

  // Compact one-liner: "Updated 3 files across Frontend, Config."
  if (mode === "compact") {
    const cats = Object.keys(diff.categories).sort();
    const catList = cats.length === 0 ? "site" :
                    cats.length === 1 ? cats[0] :
                    cats.length === 2 ? `${cats[0]} + ${cats[1]}` :
                    `${cats[0]}, ${cats[1]}, +${cats.length - 2} more`;
    return (
      <div className={`flex items-center gap-2 text-sm text-muted-foreground ${className}`}>
        <Check className="w-4 h-4 text-green-400" aria-hidden />
        <span>
          Updated <strong className="text-foreground">{diff.total_changed} file{diff.total_changed === 1 ? "" : "s"}</strong>
          {" "}across <span className="text-foreground">{catList}</span>.
        </span>
      </div>
    );
  }

  // Expanded panel — category roll-up + collapsible file list.
  const displayCategories: Category[] = showUntouched
    ? [...ALL_CATEGORIES]
    : (Object.keys(diff.categories) as Category[]).sort();

  return (
    <div className={`rounded-xl border border-border bg-card/60 p-4 space-y-3 ${className}`}>
      <div className="flex items-baseline justify-between">
        <h4 className={type.heading.s}>What changed</h4>
        <span className={`${type.caption} text-muted-foreground`}>
          {diff.total_changed} file{diff.total_changed === 1 ? "" : "s"} • snapshot saved
        </span>
      </div>

      <div className="space-y-0.5 divide-y divide-border/40">
        {displayCategories.map((cat) => (
          <CategoryRow
            key={cat}
            name={cat}
            count={diff.categories[cat] ?? 0}
            total={Math.max(diff.total_changed, 1)}
          />
        ))}
      </div>

      <button
        type="button"
        onClick={() => setFilesOpen((o) => !o)}
        aria-expanded={filesOpen}
        className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
      >
        <motion.span
          animate={{ rotate: filesOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="inline-flex"
        >
          <ChevronDown className="w-3.5 h-3.5" aria-hidden />
        </motion.span>
        <span>{filesOpen ? "Hide file list" : "Show file list"}</span>
      </button>

      <AnimatePresence initial={false}>
        {filesOpen && (
          <motion.div
            key="files"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <ul className="space-y-1.5 pt-1 text-sm">
              {diff.files.map((f) => (
                <li key={f.path} className="flex items-center justify-between gap-3">
                  <span className="flex items-center gap-2 min-w-0">
                    <StatusIcon status={f.status} />
                    <code className="font-mono text-xs text-foreground/85 truncate">{f.path}</code>
                  </span>
                  {f.status !== "deleted" && (
                    <LineDelta added={f.lines_added} removed={f.lines_removed} />
                  )}
                </li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
