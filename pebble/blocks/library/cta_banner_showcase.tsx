"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import MagneticButton from "@/components/motion/MagneticButton";

export default function CtaBannerShowcase() {
  return (
    <section className="relative overflow-hidden min-h-[420px] flex items-center justify-center">
      {/* Full-bleed backdrop — decorative background image */}
      <div className="absolute inset-0">
        <Image
          src="{{bg_image}}"
          alt=""
          fill
          className="object-cover"
        />
        {/* Dark overlay — ensures ≥4.5:1 contrast for white text over photo */}
        <div className="absolute inset-0 bg-black/60" />
      </div>

      {/* Content — center-anchored column */}
      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center py-16 md:py-20">

        {/* Headline */}
        <h2 className="text-white text-4xl md:text-6xl font-semibold leading-tight tracking-tight">
          <RevealWords>{{headline}}</RevealWords>
        </h2>

        {/* Subheadline — optional reassurance line */}
        <p className="text-white/80 text-lg mt-4 leading-relaxed">
          {{subheadline}}
        </p>

        {/* CTA row */}
        <div className="flex flex-wrap gap-4 justify-center mt-8">
          {/* Primary CTA */}
          <MagneticButton
            href="#contact"
            className="inline-flex items-center justify-center bg-{{accent}} text-{{accent_fg}} px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] hover:opacity-90 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-{{accent}} focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
          >
            {{cta_primary}}
          </MagneticButton>

          {/* Tap-to-call — phone CTA */}
          <a
            href="tel:{{phone}}"
            className="inline-flex items-center justify-center gap-2 bg-white/10 text-white px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] border border-white/30 hover:bg-white/20 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              width="20"
              height="20"
              aria-hidden="true"
            >
              <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
            </svg>
            {{phone}}
          </a>
        </div>

      </div>
    </section>
  );
}
