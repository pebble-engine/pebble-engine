"use client";

/**
 * FirstBuildCelebration — confetti + upgrade-CTA shown when a free
 * user finishes their first build. The post-build dopamine spike is
 * the single highest-converting moment in the funnel — leverage it
 * instead of letting it pass quietly.
 *
 * Triggered by ReadyPhase when:
 *   - the user's project count is exactly 1 (genuinely first build)
 *   - AND localStorage has NOT seen pebble.first_build_celebrated
 *
 * One-shot — sets the localStorage flag on first mount so a refresh
 * or re-mount doesn't re-celebrate.
 */

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight, X } from "lucide-react";
import { PebletMascot } from "@/components/peblet-mascot";

export type FirstBuildCelebrationProps = {
  open:    boolean;
  onClose: () => void;
};

const CONFETTI_COLORS = ["#3054ff", "#c76e3a", "#4b6548", "#5b6f4a", "#205661"];

export function FirstBuildCelebration({ open, onClose }: FirstBuildCelebrationProps) {
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    if (open) {
      // Small delay so the modal animates in before confetti fires.
      const t = setTimeout(() => setShowConfetti(true), 300);
      return () => clearTimeout(t);
    } else {
      setShowConfetti(false);
    }
  }, [open]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[110] bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
          onClick={onClose}
        >
          {showConfetti && (
            <div aria-hidden className="absolute inset-0 pointer-events-none overflow-hidden">
              {Array.from({ length: 24 }).map((_, i) => (
                <motion.div
                  key={i}
                  initial={{ y: -20, x: `${Math.random() * 100}vw`, opacity: 0 }}
                  animate={{ y: "110vh", opacity: [0, 1, 1, 0] }}
                  transition={{ duration: 3 + Math.random() * 2, delay: Math.random() * 0.5, ease: "easeOut" }}
                  className="absolute w-3 h-3 rounded-full"
                  style={{ background: CONFETTI_COLORS[i % CONFETTI_COLORS.length] }}
                />
              ))}
            </div>
          )}

          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.3 }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-md bg-card border border-border rounded-3xl shadow-2xl overflow-hidden"
          >
            <button
              type="button"
              onClick={onClose}
              className="absolute top-3 right-3 p-1.5 rounded-md text-muted-foreground hover:bg-accent hover:text-foreground z-10"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="p-8 text-center bg-gradient-to-br from-primary/10 via-violet-500/5 to-amber-500/10">
              <PebletMascot size="lg" animate />
              <p className="text-[10px] uppercase tracking-widest font-bold text-primary mt-4">
                Built it. Shipped it.
              </p>
              <h2 className="text-3xl font-extrabold text-foreground mt-2 tracking-tight">
                Your first site is live!
              </h2>
              <p className="text-sm text-muted-foreground mt-3 max-w-sm mx-auto">
                You can keep editing this for free forever. When you're ready to make it real — custom domain, real form emails, integrations — Starter is $19.99/mo.
              </p>
            </div>

            <div className="p-6 space-y-2">
              <Link
                href="/pricing"
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-full bg-primary text-primary-foreground font-bold text-sm hover:opacity-95"
              >
                <Sparkles className="w-4 h-4" />
                See what Starter unlocks
                <ArrowRight className="w-4 h-4" />
              </Link>
              <button
                type="button"
                onClick={onClose}
                className="w-full py-2 text-xs font-semibold text-muted-foreground hover:text-foreground"
              >
                Keep editing
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
