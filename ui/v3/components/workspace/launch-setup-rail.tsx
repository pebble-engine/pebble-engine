"use client";

/**
 * LaunchSetupRail — compact checklist rendered in the left sidebar.
 *
 * Extracted from the old LaunchSetupPanel (right-rail, edit-phase.tsx) as
 * part of the Phase 56a preview-first layout restructure. Key differences:
 *
 *   - No "Go Live" button (that lives in the TopNav Publish slot).
 *   - No BuildIntegrityChecklist (removed from this surface).
 *   - No dependency-graph prose ("Unlocks after: …").
 *   - Tight single-row layout: checkbox glyph + label only.
 *   - Three items dropped per Marc's explicit request: project_name,
 *     hosting, business_email — those belong in a future Settings page.
 *   - Collapsible header with item-count badge.
 *
 * Renders nothing when plan is null (sidebar renders it on every page so
 * we need a graceful no-op for non-design phases).
 */

import { useState } from "react";
import { Check, Circle, ChevronDown } from "lucide-react";
import { type PebblePlan, type PebbleSetupItem } from "@/lib/state";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

// Items Marc explicitly asked to drop from the sidebar rail.
const DROPPED_IDS = new Set(["project_name", "hosting", "business_email"]);

// Display order: auto-done items first (confidence signals), then actionable.
const ITEM_ORDER = [
  "pages",
  "forms",
  "seo_basics",
  "accessibility",
  "logo_photos",
  "website_address",
  "booking",
  "payments",
  "analytics",
  "language_region",
  "publish",
];

function sortItems(items: PebbleSetupItem[]): PebbleSetupItem[] {
  return [...items].sort((a, b) => {
    const ai = ITEM_ORDER.indexOf(a.id);
    const bi = ITEM_ORDER.indexOf(b.id);
    // Known items in prescribed order; unknown items go last.
    const an = ai === -1 ? 999 : ai;
    const bn = bi === -1 ? 999 : bi;
    return an - bn;
  });
}

type Props = {
  plan: PebblePlan | null;
  className?: string;
};

export function LaunchSetupRail({ plan, className = "" }: Props) {
  const items = plan
    ? sortItems(plan.setup_needs.filter((s) => !DROPPED_IDS.has(s.id)))
    : [];

  const pendingCount = items.filter((s) => s.status !== "auto").length;

  // Default: expanded when any items still need attention, collapsed when
  // everything is auto-done (the all-green state is a confidence signal,
  // not a to-do list).
  const [isExpanded, setIsExpanded] = useState(() => pendingCount > 0);

  if (!plan) return null;

  return (
    <section className={`mt-2 ${className}`}>
      {/* Section divider */}
      <div className="mx-3 border-t border-border mb-2" />

      {/* Collapsible header */}
      <button
        onClick={() => setIsExpanded((v) => !v)}
        className={`${interactions.chip} w-full flex items-center justify-between px-3 py-1.5 rounded-lg text-left`}
        aria-expanded={isExpanded}
      >
        <span className={`${type.eyebrow} text-muted-foreground`}>Launch Setup</span>
        <div className="flex items-center gap-1.5">
          {pendingCount > 0 && (
            <span className="text-[10px] font-bold bg-spark/15 text-spark-deep px-1.5 py-0.5 rounded-full">
              {pendingCount}
            </span>
          )}
          <ChevronDown
            className={`w-3 h-3 text-muted-foreground transition-transform duration-200 ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
        </div>
      </button>

      {/* Item list — inline expansion, no drawer */}
      {isExpanded && (
        <ul className="mt-1 flex flex-col gap-0.5">
          {items.map((item) => (
            <li key={item.id} className="flex items-center gap-2 px-3 py-1">
              {item.status === "auto" ? (
                <Check className="w-3.5 h-3.5 text-earth-deep shrink-0" />
              ) : (
                <Circle className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
              )}
              <span
                className={`text-xs leading-snug ${
                  item.status === "auto"
                    ? "text-muted-foreground line-through"
                    : "text-foreground"
                }`}
              >
                {item.label}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
