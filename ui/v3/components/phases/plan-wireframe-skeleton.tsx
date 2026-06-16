"use client";

import { motion } from "framer-motion";
import { getBrief } from "@/lib/state";
import { type } from "@/lib/type";
import { EASE_CINEMATIC, STANDARD_S, withReducedMotion } from "@/lib/motion";
import { useMemo } from "react";

const pulse = {
  initial: { opacity: 0.35 },
  animate: { opacity: [0.35, 0.7, 0.35] },
  transition: { duration: 1.8, repeat: Infinity, ease: EASE_CINEMATIC },
};

type Props = {
  /** Override brief fields when parent already has them in state */
  businessName?: string;
  goalLabel?: string;
};

export function PlanWireframeSkeleton({ businessName, goalLabel }: Props) {
  const brief = getBrief();
  const name =
    businessName
    || (brief.business_name as string)
    || "Your business";
  const funcs = (brief.site_functions as string[]) || ["leads"];
  const showBooking = funcs.includes("booking");
  const showShop = funcs.includes("ecommerce");
  const goal =
    goalLabel
    || (showBooking ? "Bookings" : showShop ? "Shop" : funcs.includes("presence") ? "Story" : "Contact");

  const safePulse = useMemo(() => withReducedMotion(pulse), []);

  return (
    <div className="w-full max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2 text-center md:text-left">
        <p className={`${type.heading.m} text-foreground`}>Sketching your plan…</p>
        <p className={`${type.body.s} text-muted-foreground`}>
          {name} · {goal} — this takes a few seconds
        </p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-4 md:p-6 shadow-[var(--shadow-1)] overflow-hidden">
        {/* Browser chrome */}
        <div className="flex items-center gap-2 mb-4">
          <span className="w-2.5 h-2.5 rounded-full bg-muted-foreground/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-muted-foreground/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-muted-foreground/20" />
          <div className="flex-1 h-6 rounded-md bg-muted/60 ml-2 max-w-xs" />
        </div>

        {/* Wireframe page */}
        <div className="rounded-xl border border-border/80 bg-background/50 p-3 space-y-3">
          <motion.div {...safePulse} className="h-8 rounded-lg bg-muted w-full max-w-md" />
          <motion.div
            {...safePulse}
            transition={{ ...safePulse.transition, delay: 0.15 }}
            className="h-32 md:h-40 rounded-xl bg-muted/80 w-full"
          />
          <div className="grid grid-cols-3 gap-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                {...safePulse}
                transition={{ ...safePulse.transition, delay: 0.2 + i * 0.1 }}
                className="h-16 rounded-lg bg-muted/70"
              />
            ))}
          </div>
          {showBooking && (
            <motion.div
              {...safePulse}
              transition={{ ...safePulse.transition, delay: 0.5 }}
              className="h-10 rounded-full bg-primary/20 w-40 mx-auto"
            />
          )}
          {!showBooking && (
            <motion.div
              {...safePulse}
              transition={{ ...safePulse.transition, delay: 0.5 }}
              className="h-10 rounded-full bg-muted w-36 mx-auto"
            />
          )}
        </div>

        <p className={`${type.mono} text-xs text-muted-foreground/70 mt-4 text-center`}>
          Wireframe preview — your real plan loads next
        </p>
      </div>

      <div className="flex flex-wrap gap-2 justify-center md:justify-start">
        {["Pages", "Style", "Setup"].map((chip, i) => (
          <motion.span
            key={chip}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: STANDARD_S, delay: i * 0.12, ease: EASE_CINEMATIC }}
            className="px-3 py-1 rounded-full border border-border text-xs text-muted-foreground bg-card"
          >
            {chip}…
          </motion.span>
        ))}
      </div>
    </div>
  );
}
