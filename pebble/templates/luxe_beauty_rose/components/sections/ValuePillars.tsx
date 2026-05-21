"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ScriptText } from "@/components/ui/ScriptText";
import {
  VALUES,
  VALUES_EYEBROW,
  VALUES_HEADLINE,
} from "@/content/site";

/**
 * ValuePillars — 3-column grid of brand promises.
 * Whitespace-heavy, italic Bodoni titles, body text in Manrope, no icons
 * (deliberately editorial — text is the design).
 */
export function ValuePillars() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="values-heading"
      className="bg-surface-container-low"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl">
          <p className="text-label mb-3">{VALUES_EYEBROW}</p>
          <h2 id="values-heading" className="text-headline">
            {VALUES_HEADLINE}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10 md:gap-12">
          {VALUES.map((value, i) => (
            <motion.div
              key={value.title}
              initial={{ opacity: 0, y: reduce ? 0 : 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-col gap-4"
            >
              <span className="text-label">0{i + 1}</span>
              <h3 className="font-display italic text-3xl md:text-4xl text-on-surface leading-tight">
                {value.title}
              </h3>
              <ScriptText className="text-2xl -mt-1 mb-1">
                {i === 0 ? "for every skin" : i === 1 ? "always" : "with care"}
              </ScriptText>
              <p className="text-body-lg">{value.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
