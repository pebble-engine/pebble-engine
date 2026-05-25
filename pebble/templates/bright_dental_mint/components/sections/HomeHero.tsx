"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "framer-motion";
import {
  HERO_IMAGE,
  HERO_HEADLINE,
  HERO_SUBHEAD,
  HERO_PRIMARY_CTA,
  HERO_PRIMARY_HREF,
  HERO_SECONDARY_CTA,
  HERO_SECONDARY_HREF,
  HERO_FOOTNOTE,
  TRUSTED_SINCE,
} from "@/content/site";

export function HomeHero() {
  const reduce = useReducedMotion();
  const chars = Array.from(HERO_HEADLINE);

  return (
    <section className="pt-28 pb-16 lg:pt-36 lg:pb-24 px-6 bg-white">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="rounded-2xl overflow-hidden shadow-lg bg-ice aspect-[4/3] lg:aspect-square relative"
        >
          <Image
            src={HERO_IMAGE}
            alt="Friendly dentist with patient"
            fill
            priority
            sizes="(max-width: 1024px) 100vw, 600px"
            className="object-cover"
          />
          <div className="absolute top-6 left-6 bg-white/90 backdrop-blur px-4 py-2 rounded-full text-xs font-semibold text-navy shadow-sm">
            {TRUSTED_SINCE}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1, ease: [0.22, 1, 0.36, 1] }}
          className="space-y-6"
        >
          <h1 className="font-[family-name:var(--font-display)] text-4xl md:text-6xl font-bold text-navy leading-tight">
            {reduce ? (
              HERO_HEADLINE
            ) : (
              <span aria-hidden="true">
                {chars.map((c, i) => (
                  <motion.span
                    key={i}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.2 + i * 0.025, ease: [0.22, 1, 0.36, 1] }}
                    className="inline-block whitespace-pre"
                  >
                    {c === " " ? " " : c}
                  </motion.span>
                ))}
              </span>
            )}
            {!reduce && <span className="sr-only">{HERO_HEADLINE}</span>}
          </h1>
          <p className="text-lg text-slate-600 max-w-xl leading-relaxed">{HERO_SUBHEAD}</p>
          <div className="flex flex-col sm:flex-row gap-4 pt-2">
            <a href={HERO_PRIMARY_HREF} className="btn-coral">{HERO_PRIMARY_CTA}</a>
            <a
              href={HERO_SECONDARY_HREF}
              className="px-6 py-4 text-center font-semibold text-navy border-2 border-navy/20 rounded-full hover:bg-navy hover:text-white transition-colors"
            >
              {HERO_SECONDARY_CTA}
            </a>
          </div>
          <div className="pt-4 text-sm text-slate-500">{HERO_FOOTNOTE}</div>
        </motion.div>
      </div>
    </section>
  );
}
