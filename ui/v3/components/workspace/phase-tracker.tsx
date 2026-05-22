"use client";

/**
 * PhaseTracker — Phase 46 (2026-05-22).
 *
 * Horizontal phase indicator that replaces the old "Your Build Plan"
 * vertical sidebar. Marc's call: the vertical phase list made the
 * surface feel like a wizard/checklist instead of a real workspace.
 * The shared dashboard sidebar (Home/Templates/Integrations/Community)
 * is now in the left rail; the per-project phase progress sits as
 * subtle breadcrumb chips at the top of the main content area.
 *
 * Renders nothing on welcome (the marketing canvas owns its own
 * chrome) or design (the editor is full-bleed by intent — adding a
 * phase rail above it crowds the preview).
 */

import React from "react";
import { motion } from "framer-motion";
import { Lightbulb, Map, Edit3, Palette, Rocket } from "lucide-react";
import type { Phase } from "@/components/phases/use-phase";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

type StepId = Phase | "features" | "setup";

type Step = {
  id:     StepId;
  label:  string;
  Icon:   typeof Lightbulb;
};

const STEPS: readonly Step[] = [
  { id: "idea",    label: "Idea",    Icon: Lightbulb },
  { id: "plan",    label: "Plan",    Icon: Map },
  { id: "draft",   label: "Draft",   Icon: Edit3 },
  { id: "design",  label: "Design",  Icon: Palette },
  { id: "publish", label: "Publish", Icon: Rocket },
];

export function PhaseTracker({
  current,
  onJump,
  buildExists,
}: {
  current: Phase;
  onJump: (target: StepId) => void;
  /** Whether a build has been generated yet — gates Design and Publish. */
  buildExists: boolean;
}) {
  // Don't render on welcome or design — the surfaces own their own chrome.
  if (current === "welcome" || current === "design") return null;

  const currentIndex = STEPS.findIndex((s) => s.id === current);

  return (
    <div className="border-b border-border bg-card/50 backdrop-blur-sm">
      <div className="max-w-5xl mx-auto px-6 py-3">
        <ol className="flex items-center gap-1 overflow-x-auto">
          {STEPS.map((step, i) => {
            const isCurrent = step.id === current;
            const isPast = i < currentIndex;
            const isReachable =
              step.id === "idea" ||
              step.id === "plan" ||
              (step.id === "draft" && currentIndex >= 2) ||
              ((step.id === "design" || step.id === "publish") && buildExists);

            return (
              <React.Fragment key={step.id}>
                <li>
                  <button
                    onClick={() => isReachable && onJump(step.id)}
                    disabled={!isReachable}
                    className={`${interactions.chip} relative flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                      isCurrent
                        ? "bg-foreground text-background"
                        : isPast
                          ? "text-foreground hover:bg-muted"
                          : isReachable
                            ? "text-muted-foreground hover:text-foreground"
                            : "text-muted-foreground/50 cursor-not-allowed"
                    }`}
                  >
                    {isCurrent && (
                      <motion.span
                        layoutId="phase-tracker-active"
                        className="absolute inset-0 rounded-full bg-foreground -z-10"
                        transition={{ type: "spring", stiffness: 380, damping: 30 }}
                      />
                    )}
                    <step.Icon className="w-3.5 h-3.5" />
                    <span className={type.label}>{step.label}</span>
                  </button>
                </li>
                {i < STEPS.length - 1 && (
                  <li aria-hidden className="text-muted-foreground/40 px-0.5">
                    <span className="text-[10px]">›</span>
                  </li>
                )}
              </React.Fragment>
            );
          })}
        </ol>
      </div>
    </div>
  );
}
