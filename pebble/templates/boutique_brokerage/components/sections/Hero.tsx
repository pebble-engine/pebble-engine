"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import {
  HERO_EYEBROW,
  HERO_HEADLINE_LINE_1,
  HERO_HEADLINE_LINE_2,
  HERO_SUBHEADLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_PRIMARY_HREF,
  HERO_CTA_SECONDARY,
  HERO_CTA_SECONDARY_HREF,
  HERO_IMAGE_URL,
  HERO_SCROLL_LABEL,
} from "@/content/site";

/**
 * Hero — full-bleed cinematic mansion image with cinematic-img filter
 * (contrast 1.1 + brightness 0.9) + 60% black overlay. Vermilion eyebrow
 * with 0.3em letter-spacing sits above an enormous two-line Unbounded
 * Black headline that uses mix-blend-overlay so it interacts with the
 * photo behind it. Two CTAs sit below; a thin vertical scroll indicator
 * with a vermilion bar marks bottom-center.
 */
export function Hero() {
  const reduce = useReducedMotion();

  const item = (delay: number) => ({
    initial: { opacity: 0, y: reduce ? 0 : 24 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.9, delay, ease: [0.16, 1, 0.3, 1] as const },
  });

  return (
    <section
      aria-label="Hero"
      className="relative isolate overflow-hidden bg-bg min-h-screen flex items-center"
    >
      {/* Full-bleed photo */}
      <div className="absolute inset-0 -z-10" aria-hidden="true">
        <Image
          src={HERO_IMAGE_URL}
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover cinematic-img"
        />
        {/* 60% black overlay */}
        <div className="absolute inset-0 bg-bg/60" />
      </div>

      <div className="page-container relative w-full pt-32 pb-32 md:pt-40 md:pb-40">
        {/* Eyebrow */}
        <motion.p
          {...item(0)}
          className="text-label mb-8"
        >
          {HERO_EYEBROW}
        </motion.p>

        {/* Headline — mix-blend-overlay so it interacts with the photo */}
        <motion.h1
          {...item(0.15)}
          className="text-mega text-fg mix-blend-overlay mb-10"
        >
          {HERO_HEADLINE_LINE_1}
          <br />
          {HERO_HEADLINE_LINE_2}
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          {...item(0.3)}
          className="text-body-lg max-w-xl mb-10"
        >
          {HERO_SUBHEADLINE}
        </motion.p>

        {/* CTAs */}
        <motion.div
          {...item(0.45)}
          className="flex flex-col sm:flex-row items-start sm:items-center gap-4"
        >
          <Button href={HERO_CTA_PRIMARY_HREF} variant="cinematic">
            {HERO_CTA_PRIMARY}
          </Button>
          <Button href={HERO_CTA_SECONDARY_HREF} variant="outline">
            {HERO_CTA_SECONDARY}
          </Button>
        </motion.div>
      </div>

      {/* Scroll indicator — vertical hairline + vermilion bar */}
      <div
        aria-hidden="true"
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-3"
      >
        <span className="text-eyebrow">{HERO_SCROLL_LABEL}</span>
        <div className="relative w-px h-16 bg-fg/30 overflow-hidden">
          <span className="absolute top-0 left-0 w-px h-1/2 bg-accent animate-pulse" />
        </div>
      </div>
    </section>
  );
}
