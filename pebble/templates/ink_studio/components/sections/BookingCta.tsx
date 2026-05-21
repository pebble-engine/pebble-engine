"use client";

import * as React from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import {
  BOOKING_EYEBROW,
  BOOKING_HEADLINE,
  BOOKING_INTRO,
  BOOKING_CTA,
  BOOKING_CTA_HREF,
  HERO_VIDEO_URL,
  HERO_POSTER_URL,
} from "@/content/site";

/**
 * BookingCta — full-bleed dark section with the hero video reused as the
 * background (per DNA `booking_cta` notes). Gold thin top + bottom rules
 * frame the centered blackletter h2 + filled gold CTA. Replays the same
 * cinematic feel as the hero, scoped to a single action.
 */
export function BookingCta() {
  const reduce = useReducedMotion();

  return (
    <section
      aria-labelledby="booking-heading"
      className="relative isolate overflow-hidden border-y border-ink-primary/40"
    >
      {/* Background — same poster image as the hero; tinted darker. */}
      <div className="absolute inset-0 -z-20" aria-hidden="true">
        <Image
          src={HERO_POSTER_URL}
          alt=""
          fill
          sizes="100vw"
          className="object-cover opacity-25"
        />
      </div>
      {HERO_VIDEO_URL ? (
        <video
          className="absolute inset-0 -z-10 h-full w-full object-cover opacity-25"
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

      <div
        className="absolute inset-0 -z-[5] bg-ink-bg/80"
        aria-hidden="true"
      />

      <div className="page-container relative py-section-mobile md:py-section-desktop">
        <motion.div
          initial={{ opacity: 0, y: reduce ? 0 : 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-2xl text-center"
        >
          <p className="text-eyebrow mb-5">{BOOKING_EYEBROW}</p>
          <h2
            id="booking-heading"
            className="text-display gold-glow-text mb-6"
          >
            {BOOKING_HEADLINE}
          </h2>
          <p className="text-body-lg mb-10">{BOOKING_INTRO}</p>
          <Button href={BOOKING_CTA_HREF} variant="primary" size="lg">
            {BOOKING_CTA}
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
