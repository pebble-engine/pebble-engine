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
  HERO_VIDEO_URL,
  HERO_POSTER_URL,
} from "@/content/site";

/**
 * Hero — full-bleed dark backdrop. The DNA prescribes a looping background
 * video; we render a `<video>` with the poster image as both the `poster`
 * attribute and a same-source `<Image>` underneath so the page still feels
 * cinematic even when the video URL is missing or blocked. Giant
 * UnifrakturCook wordmark sits centered with a stacked gold text-shadow
 * (the DNA's signature gold-glow). Dual gold CTAs (outline + filled) sit
 * below an Bebas eyebrow.
 */
export function Hero() {
  const reduce = useReducedMotion();

  const item = (delay: number) => ({
    initial: { opacity: 0, y: reduce ? 0 : 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.9, delay, ease: [0.16, 1, 0.3, 1] as const },
  });

  return (
    <section
      aria-label="Hero"
      className="relative isolate overflow-hidden min-h-[88vh] md:min-h-[92vh] flex items-center"
    >
      {/* Background — poster image is always rendered; the <video> sits on
          top once loaded and never goes transparent on failure. */}
      <div className="absolute inset-0 -z-20" aria-hidden="true">
        <Image
          src={HERO_POSTER_URL}
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-40"
        />
      </div>

      {HERO_VIDEO_URL ? (
        <video
          className="absolute inset-0 -z-10 h-full w-full object-cover opacity-40"
          autoPlay
          muted
          loop
          playsInline
          poster={HERO_POSTER_URL}
          aria-hidden="true"
        >
          <source src={HERO_VIDEO_URL} type="video/mp4" />
        </video>
      ) : null}

      {/* Dual gradient mask — top + bottom into pitch black for legibility. */}
      <div
        className="absolute inset-0 -z-[5] bg-gradient-to-b from-ink-bg via-transparent to-ink-bg"
        aria-hidden="true"
      />
      <div
        className="absolute inset-0 -z-[4] bg-gradient-to-r from-ink-bg/80 via-transparent to-ink-bg/80"
        aria-hidden="true"
      />

      <div className="page-container relative w-full pt-32 pb-section-mobile md:pt-40 md:pb-section-desktop">
        <div className="mx-auto max-w-4xl text-center">
          <motion.p {...item(0)} className="text-eyebrow mb-8">
            {HERO_EYEBROW}
          </motion.p>

          {/* Giant blackletter wordmark with gold-glow text-shadow */}
          <motion.h1
            {...item(0.1)}
            className="text-display-mega gold-glow-text-strong mb-4 animate-gold-pulse"
          >
            <span className="block">{HERO_HEADLINE_LINE_1}</span>
            <span className="block">{HERO_HEADLINE_LINE_2}</span>
          </motion.h1>

          <motion.p
            {...item(0.3)}
            className="text-body-lg max-w-2xl mx-auto mb-12 text-ink-text-secondary"
          >
            {HERO_SUBHEADLINE}
          </motion.p>

          <motion.div
            {...item(0.5)}
            className="flex flex-col sm:flex-row items-center justify-center gap-4"
          >
            <Button href={HERO_CTA_PRIMARY_HREF} variant="primary" size="lg">
              {HERO_CTA_PRIMARY}
            </Button>
            <Button href={HERO_CTA_SECONDARY_HREF} variant="secondary" size="lg">
              {HERO_CTA_SECONDARY}
            </Button>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
