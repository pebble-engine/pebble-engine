"use client";
import { motion } from "framer-motion";
import { RefCode } from "@/components/ui/RefCode";
import { PROCESS_STEPS } from "@/content/site";

/**
 * Five-step workflow grid per the DNA's section_flow.process spec. Each card
 * has a circle-number badge floating half-outside the top edge, stencil
 * heading, and 100ms stagger entrance.
 */
export function Process() {
  if (!PROCESS_STEPS.length) return null;

  return (
    <section id="process" className="relative py-20 sm:py-28 border-t border-white/5">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mb-16 max-w-2xl">
          <RefCode accent>// WF-001</RefCode>
          <h2 className="mt-3 stencil text-5xl sm:text-6xl">THE WORKFLOW</h2>
          <p className="mt-4 text-base text-muted">
            Five steps. No surprises. You approve every dollar before we turn a wrench.
          </p>
        </div>

        <ol className="grid gap-6 pt-8 sm:grid-cols-2 lg:grid-cols-5 lg:gap-4">
          {PROCESS_STEPS.map((step, i) => (
            <motion.li
              key={step.ref}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1, ease: "easeOut" }}
              className="relative border border-white/10 bg-card/40 p-6"
            >
              {/* Circle-number badge floating half-outside the top edge */}
              <span className="absolute -top-5 left-6 inline-flex h-10 w-10 items-center justify-center rounded-full bg-primary text-bg font-mono text-sm font-bold tracking-tight">
                {String(step.step).padStart(2, "0")}
              </span>
              <div className="mt-4">
                <RefCode>{step.ref}</RefCode>
                <h3 className="mt-2 stencil-filled text-xl">{step.title}</h3>
                <p className="mt-2 text-sm text-muted">{step.description}</p>
              </div>
            </motion.li>
          ))}
        </ol>
      </div>
    </section>
  );
}
