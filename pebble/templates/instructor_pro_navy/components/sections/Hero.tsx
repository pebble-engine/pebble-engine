"use client";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/Button";
import { PulseDot } from "@/components/ui/PulseDot";
import {
  HERO_EYEBROW,
  HERO_HEADLINE_LINE_1,
  HERO_HEADLINE_LINE_2,
  HERO_HEADLINE_LINE_3_GOLD,
  HERO_HEADLINE_LINE_4,
  HERO_TAGLINE,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
  HERO_VIDEO_URL,
  HERO_VIDEO_POSTER,
} from "@/content/site";

/**
 * Full-bleed looping video hero per training_authority DNA:
 * - Autoplay-muted-loop video background with double-gradient masking
 *   (black -> bg from bottom, and dark sides)
 * - Tracked eyebrow pill with live red pulse dot
 * - Four-line Outfit-black headline; line 3 uses gold-gradient text fill
 * - All-caps DM Sans tagline with 0.12em tracking
 * - Dual pill CTAs with hover scale-1.02 (built into Button)
 */
export function Hero() {
  return (
    <section className="relative isolate flex min-h-[100vh] items-center overflow-hidden pt-32 pb-20 sm:pt-36 sm:pb-24">
      {/* Background video — full-bleed under double-gradient masks */}
      <div className="absolute inset-0 -z-10">
        <video
          autoPlay
          muted
          loop
          playsInline
          poster={HERO_VIDEO_POSTER}
          className="h-full w-full object-cover"
          aria-hidden="true"
        >
          <source src={HERO_VIDEO_URL} type="video/mp4" />
        </video>
        {/* Vertical gradient: black at bottom -> bg */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/55 to-bg" />
        {/* Horizontal gradient: black sides */}
        <div className="absolute inset-0 bg-[linear-gradient(90deg,hsl(var(--bg))/0.85,transparent_25%,transparent_75%,hsl(var(--bg))/0.85)]" />
      </div>

      <div className="relative z-10 mx-auto max-w-6xl px-6 text-center">
        {/* Eyebrow pill — live red pulse dot + tracked label */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="mb-8 inline-flex items-center gap-2.5 rounded-full border border-accent/40 bg-accent/10 px-4 py-1.5 backdrop-blur"
        >
          <PulseDot />
          <span className="text-[11px] font-bold uppercase tracking-wide-15 text-accent">
            {HERO_EYEBROW}
          </span>
        </motion.div>

        {/* H1 — four lines, line 3 is gold-gradient */}
        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.05 }}
          className="font-display font-black uppercase leading-[0.95] tracking-headline text-fg text-5xl sm:text-7xl lg:text-8xl"
          style={{ textShadow: "0 1px 30px rgba(0,0,0,0.55)" }}
        >
          <span className="block">{HERO_HEADLINE_LINE_1}</span>
          <span className="block">{HERO_HEADLINE_LINE_2}</span>
          <span className="block text-gold-gradient">{HERO_HEADLINE_LINE_3_GOLD}</span>
          <span className="block">{HERO_HEADLINE_LINE_4}</span>
        </motion.h1>

        {/* Tagline — all-caps DM Sans with wide tracking */}
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut", delay: 0.25 }}
          className="mx-auto mt-7 max-w-3xl text-xs font-bold uppercase tracking-wide-12 text-fg/85 sm:text-sm"
        >
          {HERO_TAGLINE}
        </motion.p>

        {/* Dual CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut", delay: 0.4 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-3"
        >
          <Button href="/contact" size="lg" variant="primary" shimmer>
            {HERO_CTA_PRIMARY}
          </Button>
          <Button href="/courses" size="lg" variant="secondary">
            {HERO_CTA_SECONDARY}
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
