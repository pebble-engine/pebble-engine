"use client";
import { motion } from "framer-motion";
import { RefCode } from "@/components/ui/RefCode";
import { TRUST_BADGES } from "@/content/site";

/**
 * Four-badge trust grid. Each card has its BADGE-0X ref code in accent yellow
 * above the badge name. Stagger entrance per DNA motion vocabulary (100ms each).
 */
export function TrustBar() {
  if (!TRUST_BADGES.length) return null;

  return (
    <section
      aria-label="Certifications"
      className="relative border-y border-white/10 bg-card/30 py-10 sm:py-12"
    >
      <div className="mx-auto max-w-6xl px-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 sm:gap-6">
          {TRUST_BADGES.map((badge, i) => (
            <motion.div
              key={badge.ref}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: "easeOut" }}
              className="border border-white/10 bg-card/40 p-4 sm:p-5"
            >
              <RefCode accent>{badge.ref}</RefCode>
              <p className="mt-2 stencil-filled text-base sm:text-lg">{badge.label}</p>
              <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
                {badge.detail}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
