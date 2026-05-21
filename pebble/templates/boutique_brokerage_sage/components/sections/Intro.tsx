"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { StatCard } from "@/components/ui/StatCard";
import { SectionDivider } from "@/components/ui/SectionDivider";
import {
  INTRO_HEADLINE_LINE_1,
  INTRO_HEADLINE_LINE_2,
  INTRO_BODY,
  STATS,
} from "@/content/site";

/**
 * Intro — two-column split. Left: "PRECISION TERRITORY." Unbounded headline
 * with vermilion underline + paragraph. Right: 2x2 stat grid (omitted when
 * STATS is empty so we never display invented numbers).
 */
export function Intro() {
  const reduce = useReducedMotion();
  const hasStats = STATS.length > 0;

  return (
    <section
      aria-labelledby="intro-heading"
      className="bg-bg"
    >
      <div className="page-container">
        <SectionDivider index="01" label="The brokerage" />
      </div>

      <div className="page-container pb-section-mobile md:pb-section-desktop">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 md:gap-16 items-start">
          {/* Left — headline + body */}
          <motion.div
            initial={{ opacity: 0, x: reduce ? 0 : -32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="lg:col-span-7"
          >
            <h2 id="intro-heading" className="text-display mb-3">
              {INTRO_HEADLINE_LINE_1}
              <br />
              {INTRO_HEADLINE_LINE_2}
            </h2>
            {/* Vermilion underline accent */}
            <div className="w-20 h-px bg-accent mb-10" aria-hidden="true" />
            <p className="text-body-lg max-w-xl">{INTRO_BODY}</p>
          </motion.div>

          {/* Right — 2x2 stat grid (only when populated) */}
          {hasStats && (
            <motion.div
              initial={{ opacity: 0, x: reduce ? 0 : 32 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.9, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="lg:col-span-5 grid grid-cols-2 gap-3 md:gap-4"
            >
              {STATS.map((stat, i) => (
                <StatCard key={i} value={stat.value} label={stat.label} />
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </section>
  );
}
