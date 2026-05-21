"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { ScriptText } from "@/components/ui/ScriptText";
import {
  HERO_HEADLINE,
  HERO_SUBHEADLINE,
  HERO_SCRIPT_ACCENT,
  HERO_CTA_PRIMARY,
  HERO_CTA_PRIMARY_HREF,
  HERO_CTA_SECONDARY,
  HERO_CTA_SECONDARY_HREF,
  HERO_IMAGE_URL,
  WORDMARK_EYEBROW,
  WORDMARK_MAIN,
} from "@/content/site";

/**
 * Hero — circular logo orb + ethereal cloud bg + dual rounded-full CTAs.
 * Italic Bodoni for the major headline. Pinyon Script for the cursive accent.
 * The hero is the foundation; no dark overlay over imagery.
 */
export function Hero() {
  const reduce = useReducedMotion();

  // Fade-in cascade for headline parts
  const item = (delay: number) => ({
    initial: { opacity: 0, y: reduce ? 0 : 16 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] as const },
  });

  return (
    <section
      aria-label="Hero"
      className="relative isolate overflow-hidden ethereal-bg"
    >
      {/* Soft ambient hero photo — low-opacity, full bleed, behind everything */}
      <div className="absolute inset-0 -z-10" aria-hidden="true">
        <Image
          src={HERO_IMAGE_URL}
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-30 mix-blend-luminosity"
        />
      </div>

      <div className="page-container relative pt-20 pb-section-mobile md:pt-32 md:pb-section-desktop">
        {/* Logo orb */}
        <motion.div
          {...item(0)}
          className="mx-auto mb-10 md:mb-12 flex h-44 w-44 md:h-56 md:w-56 items-center justify-center rounded-full glass-card-strong vapor-shadow"
        >
          <div className="flex flex-col items-center leading-none">
            <span className="font-script text-3xl md:text-4xl text-tertiary -mb-2">
              {WORDMARK_EYEBROW}
            </span>
            <span className="font-display text-2xl md:text-3xl tracking-[0.18em] uppercase text-on-surface">
              {WORDMARK_MAIN}
            </span>
          </div>
        </motion.div>

        {/* Headline */}
        <div className="mx-auto max-w-3xl text-center">
          <motion.p
            {...item(0.1)}
            className="text-label mb-5"
          >
            Atelier of luxury beauty
          </motion.p>

          <motion.h1
            {...item(0.2)}
            className="text-display mb-2"
          >
            {HERO_HEADLINE}
          </motion.h1>

          <motion.div {...item(0.3)}>
            <ScriptText className="text-3xl md:text-4xl text-tertiary block mb-6">
              {HERO_SCRIPT_ACCENT}
            </ScriptText>
          </motion.div>

          <motion.p
            {...item(0.4)}
            className="text-body-lg max-w-2xl mx-auto mb-10"
          >
            {HERO_SUBHEADLINE}
          </motion.p>

          <motion.div
            {...item(0.5)}
            className="flex flex-col sm:flex-row items-center justify-center gap-3"
          >
            <Button href={HERO_CTA_PRIMARY_HREF} variant="primary">
              {HERO_CTA_PRIMARY}
            </Button>
            <Button href={HERO_CTA_SECONDARY_HREF} variant="secondary">
              {HERO_CTA_SECONDARY}
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
