"use client";
import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/Button";
import { GlowOrb } from "@/components/ui/GlowOrb";
import {
  HERO_HEADLINE_TOP,
  HERO_HEADLINE_ACCENT,
  HERO_SUBLINE_PREFIX,
  HERO_SUBLINE_SUFFIX,
  HERO_ROTATING_WORDS,
  HERO_CTA_PRIMARY,
  HERO_CTA_SECONDARY,
  RATING_VALUE,
  RATING_COUNT,
  TRUST_BADGES,
  PHONE,
} from "@/content/site";

export function Hero() {
  const [wordIndex, setWordIndex] = useState(0);

  // Cycle the rotating subline word every 2.4s.
  useEffect(() => {
    if (HERO_ROTATING_WORDS.length <= 1) return;
    const id = window.setInterval(
      () => setWordIndex((i) => (i + 1) % HERO_ROTATING_WORDS.length),
      2400,
    );
    return () => window.clearInterval(id);
  }, []);

  const currentWord = HERO_ROTATING_WORDS[wordIndex] ?? "";

  return (
    <section className="relative isolate overflow-hidden pt-32 pb-20 sm:pt-40 sm:pb-28">
      {/* Background image — sits behind the glow orbs. Placeholder until the
          customer drops their own asset into /public/images/hero/. */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-bg via-bg/95 to-bg" />
        <Image
          src="https://images.unsplash.com/photo-1416879595882-3373a0480b5b?auto=format&fit=crop&w=2400&q=70"
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-40"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-bg/85 via-bg/70 to-bg" />
      </div>

      {/* Three blurred glow orbs — auto-hidden on mobile via .glow-orb */}
      <GlowOrb className="top-10 -left-32 h-[600px] w-[600px]" color="primary" />
      <GlowOrb className="top-40 right-0 h-[500px] w-[500px]" color="accent" />
      <GlowOrb className="bottom-0 left-1/3 h-[500px] w-[500px]" color="secondary" />

      <div className="relative z-10 mx-auto max-w-5xl px-6 text-center">
        {/* Primary CTA pill — ABOVE the headline, per DNA */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="mb-7 inline-flex"
        >
          <Button href="/contact" size="lg" shimmer>
            <SparkIcon />
            {HERO_CTA_PRIMARY}
          </Button>
        </motion.div>

        {/* H1 — Inter wins (display font is for accent only per project rules) */}
        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut", delay: 0.05 }}
          className="font-display text-5xl font-bold leading-[1.05] tracking-tight text-fg sm:text-7xl"
          style={{ textShadow: "0 1px 30px rgba(0,0,0,0.45)" }}
        >
          <span className="block">{HERO_HEADLINE_TOP}</span>
          <span className="block gradient-text">{HERO_HEADLINE_ACCENT}</span>
        </motion.h1>

        {/* Rotating subline */}
        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
          className="mx-auto mt-6 max-w-2xl text-base text-body sm:text-lg"
        >
          {HERO_SUBLINE_PREFIX}{" "}
          <span
            key={currentWord}
            className="inline-block font-semibold text-primary animate-[fade-in_0.4s_ease-out]"
            style={{ animation: "fadeIn 0.5s ease-out" }}
          >
            {currentWord}
          </span>{" "}
          {HERO_SUBLINE_SUFFIX}
        </motion.p>

        {/* Secondary CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: "easeOut", delay: 0.3 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-3"
        >
          <Button href="/services" variant="secondary" size="lg">
            See Services
          </Button>
          <Button href={`tel:${PHONE.replace(/[^+\d]/g, "")}`} variant="ghost" size="lg">
            <PhoneIcon />
            {HERO_CTA_SECONDARY}
          </Button>
        </motion.div>

        {/* Proof scaffold: rating chip + trust badges */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mt-10 flex flex-col items-center gap-4"
        >
          <div className="inline-flex items-center gap-2.5 rounded-full border border-border bg-card/60 px-4 py-2 backdrop-blur">
            <span className="flex" aria-label={`${RATING_VALUE} out of 5 stars`}>
              {Array.from({ length: 5 }).map((_, i) => (
                <StarIcon key={i} />
              ))}
            </span>
            <span className="text-sm font-semibold text-fg">{RATING_VALUE}</span>
            <span className="text-sm text-muted">({RATING_COUNT} reviews)</span>
          </div>
          <ul className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2">
            {TRUST_BADGES.map((badge) => (
              <li key={badge} className="inline-flex items-center gap-1.5 text-sm text-body">
                <CheckIcon />
                {badge}
              </li>
            ))}
          </ul>
        </motion.div>
      </div>

      {/* Local keyframes for the rotating word fade */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </section>
  );
}

function StarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="#CA8A04" aria-hidden="true">
      <path d="M12 2 14.85 8.78 22 9.27l-5.47 4.73L18.18 21 12 17.27 5.82 21l1.65-6.99L2 9.27l7.15-.49L12 2z" />
    </svg>
  );
}
function CheckIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-primary"
      aria-hidden="true"
    >
      <path d="M20 6 9 17l-5-5" />
    </svg>
  );
}
function SparkIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M12 2 14 9l7 2-7 2-2 7-2-7-7-2 7-2 2-7z" />
    </svg>
  );
}
function PhoneIcon() {
  return (
    <svg
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}
