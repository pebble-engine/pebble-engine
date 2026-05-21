"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import {
  HERO_EYEBROW,
  HERO_HEADLINE_LINE_1,
  HERO_HEADLINE_LINE_2,
  HERO_SUBHEADLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_PRIMARY_HREF,
  HERO_CTA_SECONDARY,
  HERO_CTA_SECONDARY_HREF,
  HERO_BADGE_TITLE,
  HERO_BADGE_SUBTITLE,
  HERO_IMAGE_URL,
  HERO_RATING,
} from "@/content/site";

/**
 * Hero — DNA's two_column_text_photo_blobs.
 * Left: eyebrow chip + Fraunces 2-line headline (ink line + crust-soft line)
 *       + body copy + dual button row + optional rating chip.
 * Right: tilted photo card with floating "Open early" badge anchored
 *        bottom-left, breaking the frame.
 * Background: cool radial gradient + two pulsing blurred blobs.
 */
export function Hero() {
  const reduce = useReducedMotion();

  const item = (delay: number) => ({
    initial: { opacity: 0, y: reduce ? 0 : 18 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] as const },
  });

  return (
    <section
      aria-label="Hero"
      className="relative isolate overflow-hidden hero-bg"
    >
      {/* Decorative blurred blobs */}
      <span
        aria-hidden="true"
        className="blob bg-crust/30 left-[-6rem] top-[-6rem] h-72 w-72"
      />
      <span
        aria-hidden="true"
        className="blob bg-honey/35 right-[-8rem] bottom-[-4rem] h-80 w-80"
        style={{ animationDelay: "1.2s" }}
      />

      <div className="page-container relative pt-16 md:pt-28 pb-section-mobile md:pb-section-desktop">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Left column — copy */}
          <div className="lg:col-span-6">
            <motion.div {...item(0)} className="mb-5">
              <EyebrowChip>{HERO_EYEBROW}</EyebrowChip>
            </motion.div>

            <motion.h1 {...item(0.1)} className="text-display mb-6">
              <span className="block text-ink">{HERO_HEADLINE_LINE_1}</span>
              <span className="block italic text-crust-soft">
                {HERO_HEADLINE_LINE_2}
              </span>
            </motion.h1>

            <motion.p
              {...item(0.2)}
              className="text-body-lg max-w-xl mb-9"
            >
              {HERO_SUBHEADLINE}
            </motion.p>

            <motion.div
              {...item(0.3)}
              className="flex flex-col sm:flex-row items-start sm:items-center gap-3"
            >
              <Button href={HERO_CTA_PRIMARY_HREF} variant="primary">
                {HERO_CTA_PRIMARY}
              </Button>
              <Button href={HERO_CTA_SECONDARY_HREF} variant="secondary">
                {HERO_CTA_SECONDARY}
              </Button>
            </motion.div>

            {HERO_RATING && (
              <motion.div
                {...item(0.4)}
                className="mt-8 inline-flex items-center gap-3 rounded-full liquid-glass px-4 py-2"
              >
                <span aria-hidden="true" className="text-honey">
                  &#9733;&#9733;&#9733;&#9733;&#9733;
                </span>
                <span className="text-sm text-ink-soft">
                  <span className="font-medium text-ink">{HERO_RATING.stars}</span>{" "}
                  on {HERO_RATING.source} · {HERO_RATING.count} reviews
                </span>
              </motion.div>
            )}
          </div>

          {/* Right column — tilted photo card with badge */}
          <div className="lg:col-span-6">
            <motion.div
              initial={{ opacity: 0, rotate: reduce ? -3 : -8, y: reduce ? 0 : 20 }}
              animate={{ opacity: 1, rotate: -3, y: 0 }}
              transition={{ duration: 0.9, ease: [0.34, 1.56, 0.64, 1] }}
              className="relative mx-auto max-w-md lg:max-w-none lg:ml-auto"
            >
              <div className="relative aspect-[4/5] overflow-hidden rounded-4xl warm-shadow-strong">
                <Image
                  src={HERO_IMAGE_URL}
                  alt=""
                  fill
                  priority
                  sizes="(min-width: 1024px) 600px, (min-width: 640px) 80vw, 100vw"
                  className="object-cover"
                />
              </div>

              {/* Floating badge — bottom-left, breaks the frame */}
              <motion.div
                initial={{ opacity: 0, rotate: 8, scale: 0.9 }}
                animate={{ opacity: 1, rotate: 2, scale: 1 }}
                transition={{ duration: 0.7, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="absolute -bottom-6 -left-6 md:-bottom-8 md:-left-10 z-10 rotate-2"
              >
                <div className="rounded-2xl bg-surface px-5 py-3 warm-shadow">
                  <p className="font-display text-lg md:text-xl text-ink leading-none">
                    {HERO_BADGE_TITLE}
                  </p>
                  <p className="text-xs uppercase tracking-[0.18em] text-honey mt-1">
                    {HERO_BADGE_SUBTITLE}
                  </p>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
