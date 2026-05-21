"use client";
import { motion } from "framer-motion";
import { MISSION_EYEBROW, MISSION_QUOTE, MISSION_BODY } from "@/content/site";

/**
 * Centered blockquote with radial-dots overlay per DNA notes. Oversized
 * quote SVG mark sits behind the blockquote; gradient hairline divider
 * separates the quote from the narrative paragraph.
 */
export function Mission() {
  return (
    <section className="relative overflow-hidden py-24 sm:py-32">
      {/* Dotted radial overlay */}
      <div className="absolute inset-0 radial-dots opacity-60" aria-hidden="true" />
      {/* Gradient masks to fade dots at edges */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,hsl(var(--bg))_75%)]" aria-hidden="true" />

      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-xs font-bold uppercase tracking-wide-15 text-accent"
        >
          {MISSION_EYEBROW}
        </motion.p>

        {/* Oversized quote mark */}
        <div className="relative mt-8" aria-hidden="true">
          <svg
            className="mx-auto h-20 w-20 text-accent/15 sm:h-28 sm:w-28"
            viewBox="0 0 32 32"
            fill="currentColor"
          >
            <path d="M9.4 9.6c-2.6 0-4.7 2.1-4.7 4.7v9.3h9.4v-9.3H8.4c0-2.3 1.8-4.1 4.1-4.1V6.7c-1.4 0-2.4.4-3.1 1zm14.1 0c-2.6 0-4.7 2.1-4.7 4.7v9.3h9.4v-9.3h-5.7c0-2.3 1.8-4.1 4.1-4.1V6.7c-1.4 0-2.4.4-3.1 1z" />
          </svg>
        </div>

        <motion.blockquote
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, delay: 0.1, ease: "easeOut" }}
          className="-mt-12 font-display text-2xl font-bold leading-snug text-fg sm:text-3xl lg:text-4xl"
        >
          &ldquo;{MISSION_QUOTE}&rdquo;
        </motion.blockquote>

        {/* Gradient hairline divider per DNA */}
        <div className="mx-auto my-10 h-px w-32 bg-gradient-to-r from-transparent via-[hsl(var(--accent-warm))] to-transparent" />

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mx-auto max-w-2xl text-base text-body sm:text-lg"
        >
          {MISSION_BODY}
        </motion.p>
      </div>
    </section>
  );
}
