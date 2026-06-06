"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroShowcase() {
  return (
    <section className="relative min-h-[100dvh] md:min-h-screen flex items-center justify-center overflow-hidden">
      {/* Full-bleed backdrop — real work photo */}
      <div className="absolute inset-0">
        <Image
          src="https://images.pexels.com/photos/8985456/pexels-photo-8985456.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
          alt="Auto Repair Done Right"
          fill
          priority
          className="object-cover"
        />
        {/* Dark gradient overlay — ensures ≥4.5:1 contrast for white text over photo */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/70" />
      </div>

      {/* Content — center-anchored column */}
      <div className="relative z-10 max-w-3xl mx-auto px-6 text-center flex flex-col items-center py-24 md:py-32">

        {/* Eyebrow — credential line */}
        <p className="text-white/80 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-56cc19">
          ASE-Certified · Fully Insured · Columbus, OH
        </p>

        {/* Headline */}
        <h1 className="text-white text-5xl md:text-7xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-e9bcdd">
          <RevealWords>Auto Repair Done Right</RevealWords>
        </h1>

        {/* Subheadline */}
        <p className="text-white/80 text-lg mt-6 leading-relaxed max-w-xl" data-pebble-id="pb-72c28e">
          Honest diagnostics, transparent inspections with photos, and loaner cars so your day keeps moving.
        </p>

        {/* CTA row */}
        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          {/* Primary CTA */}
          <MagneticButton
            href="#contact"
            className="inline-flex items-center justify-center bg-red-700 text-slate-50 px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] hover:opacity-90 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-700 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
          >
            Schedule Service
          </MagneticButton>

          {/* Tap-to-call — phone CTA */}
          <a
            href="tel:(614) 555-0192"
            className="inline-flex items-center justify-center gap-2 bg-white/10 text-white px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] border border-white/30 hover:bg-white/20 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" data-pebble-id="pb-758d87">
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
            (614) 555-0192
          </a>
        </div>

        {/* Trust strip */}
        <div className="mt-8 pt-6 border-t border-white/20">
          <p className="text-white/70 text-xs font-medium uppercase tracking-widest" data-pebble-id="pb-a13840">
            ASE-Certified • Fully Insured • Loaner Cars Available
          </p>
        </div>

      </div>
    </section>
  );
}
