"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import { FEATURES, FEATURES_EYEBROW, FEATURES_HEADLINE } from "@/content/site";

/**
 * Features — DNA's three_card_emoji_grid.
 * Three rounded-4xl cards on the alt-cream band with intentionally analog
 * emoji icons (the DNA forbids icon fonts here — emojis are warmer), Fraunces
 * titles, and short one-line descriptions.
 */
export function Features() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="features-heading"
      className="bg-cream-alt"
    >
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="mb-12 md:mb-16 max-w-2xl">
          <EyebrowChip className="mb-4">{FEATURES_EYEBROW}</EyebrowChip>
          <h2 id="features-heading" className="text-headline">
            {FEATURES_HEADLINE}
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-7">
          {FEATURES.map((feature, i) => (
            <motion.article
              key={feature.title}
              initial={{ opacity: 0, y: reduce ? 0 : 28 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.7, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="rounded-4xl bg-surface p-8 md:p-10 warm-shadow"
            >
              <div
                aria-hidden="true"
                className="mb-6 inline-flex h-14 w-14 items-center justify-center rounded-full bg-cream-alt text-3xl"
              >
                {feature.emoji}
              </div>
              <h3 className="font-display text-2xl md:text-3xl text-ink leading-tight mb-3">
                {feature.title}
              </h3>
              <p className="text-body-lg">{feature.description}</p>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
}
