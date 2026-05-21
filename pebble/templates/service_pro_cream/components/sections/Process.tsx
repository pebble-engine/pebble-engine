"use client";
import { motion } from "framer-motion";
import { PROCESS_STEPS } from "@/content/site";

export function Process() {
  if (!PROCESS_STEPS.length) return null;

  return (
    <section id="process" className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
            How it works
          </p>
          <h2 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
            Simple. Honest. <span className="gradient-text">Reliable.</span>
          </h2>
        </div>

        <ol className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {PROCESS_STEPS.map((step, i) => (
            <motion.li
              key={step.step}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: i * 0.08, ease: "easeOut" }}
              className="glass-card relative rounded-2xl p-6 sm:p-7"
            >
              <span className="font-display text-5xl font-bold text-primary/30">
                {String(step.step).padStart(2, "0")}
              </span>
              <h3 className="mt-3 font-display text-xl font-semibold tracking-tight text-fg">
                {step.title}
              </h3>
              <p className="mt-2 text-sm text-muted">{step.description}</p>
            </motion.li>
          ))}
        </ol>
      </div>
    </section>
  );
}
