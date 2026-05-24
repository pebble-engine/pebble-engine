"use client";

/**
 * PaywallModal — surfaces a 402 "insufficient credits" response from
 * the engine with a clean upgrade/templates path (2026-05-24).
 *
 * Marc 2026-05-24 Free tier restructure: /api/generate now refuses
 * builds when the user can't afford the 10-credit cost. The 402
 * response carries enough metadata to render a real explanation
 * (balance, needed, what alternatives exist). This modal renders
 * that explanation as a non-dismissable choice (or dismissable —
 * "Maybe later") with the Peblet mascot to soften the moment.
 *
 * Triggered by the workspace shell when it catches a 402 from the
 * build stream — see workspace-shell.tsx for the wiring.
 */

import { useRouter } from "next/navigation";
import { Sparkles, X, Rocket } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { PebletMascot } from "@/components/peblet-mascot";
import { type } from "@/lib/type";

export type PaywallReason = {
  balance:       number | null;
  needed:        number;
  /** Action identifier (e.g. "full_engine_build"). Lets future
   *  callers pass different copy per action without forking this
   *  component. */
  action?:       string;
  /** Server-provided message. Always shown if present. */
  message?:      string;
};

export function PaywallModal({
  open,
  reason,
  onClose,
}: {
  open:    boolean;
  reason:  PaywallReason | null;
  onClose: () => void;
}) {
  const router = useRouter();
  const balance = reason?.balance ?? 0;
  const needed = reason?.needed ?? 10;
  const short = Math.max(0, needed - balance);

  return (
    <AnimatePresence>
      {open && reason && (
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
            className="relative w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
          >
            {/* Close — "Maybe later" affordance. Some users want to
                think about it; non-modal dismissal respects that. */}
            <button
              type="button"
              onClick={onClose}
              className="absolute top-3 right-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground z-10"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Hero — soft gradient + Peblet face + headline */}
            <div className="relative p-7 pb-5 bg-gradient-to-br from-primary/12 via-violet-500/6 to-amber-500/8 flex flex-col items-center text-center">
              <div aria-hidden className="pointer-events-none absolute -top-10 -left-10 w-40 h-40 rounded-full bg-primary/20 blur-3xl" />
              <div aria-hidden className="pointer-events-none absolute -bottom-12 -right-10 w-40 h-40 rounded-full bg-amber-500/15 blur-3xl" />
              <div className="relative">
                <PebletMascot size="md" animate />
              </div>
              <p className={`${type.mono} relative mt-3 text-[10px] uppercase tracking-widest font-bold text-primary`}>
                A bit more needed
              </p>
              <h2 className={`${type.heading.l} relative text-foreground mt-1`}>
                {short > 0
                  ? `${short} more credit${short === 1 ? "" : "s"} to start this build`
                  : "Credits needed to start this build"}
              </h2>
              <p className={`${type.body.s} relative text-muted-foreground mt-2 max-w-sm`}>
                {reason.message ||
                  `A full engine build costs ${needed} credits and you have ${balance}. Pick a plan to keep building, or start from a template (those only cost 1).`}
              </p>
            </div>

            {/* Credit math row — visual confirmation of where they
                stand, so the ask doesn't feel arbitrary. */}
            <div className="px-7 py-4 border-t border-border bg-muted/30">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground">Balance</p>
                  <p className={`${type.heading.m} text-foreground mt-0.5`}>{balance}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground">Needed</p>
                  <p className={`${type.heading.m} text-foreground mt-0.5`}>{needed}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-widest text-muted-foreground">Short</p>
                  <p className={`${type.heading.m} text-primary mt-0.5`}>{short}</p>
                </div>
              </div>
            </div>

            {/* Action row — three paths, ordered by intent. Upgrade
                first (paid intent), then templates (free path that
                actually works for them today), then cancel. */}
            <div className="p-7 pt-5 space-y-2">
              <button
                type="button"
                onClick={() => { onClose(); router.push("/pricing"); }}
                className="group w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-primary text-primary-foreground font-bold text-sm hover:opacity-95 transition-opacity"
              >
                <Sparkles className="w-4 h-4" />
                Upgrade for more credits
              </button>
              <button
                type="button"
                onClick={() => { onClose(); router.push("/templates"); }}
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-card border border-border text-foreground font-semibold text-sm hover:bg-accent transition-colors"
              >
                <Rocket className="w-4 h-4" />
                Start from a template (1 credit)
              </button>
              <button
                type="button"
                onClick={onClose}
                className="w-full py-2 text-xs font-semibold text-muted-foreground hover:text-foreground transition-colors"
              >
                Maybe later
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
