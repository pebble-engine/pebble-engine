"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroTradePro() {
  return (
    <section className="relative min-h-[100dvh] md:min-h-screen flex items-center overflow-hidden bg-stone-50">
      {/* Full-bleed backdrop — real work photo */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={30}>
          <Image
            src="https://images.pexels.com/photos/9690090/pexels-photo-9690090.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Landscape Design & Lawn Care for Raleigh Homes"
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        {/* Dark gradient overlay — ensures ≥4.5:1 contrast for headline over photo */}
        <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-black/20 md:to-transparent" />
      </div>

      {/* Content — left-anchored column */}
      <div className="relative z-10 container mx-auto max-w-6xl px-6 md:px-8 py-24 md:py-32">
        <div className="max-w-lg">

          {/* Eyebrow — credential line */}
          <p className="text-green-700 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-c429ac">
            Licensed & Insured · Serving the Triangle Area
          </p>

          {/* Headline */}
          <h1 className="text-white text-5xl md:text-7xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-c664c7">
            <RevealWords>Landscape Design & Lawn Care for Raleigh Homes</RevealWords>
          </h1>

          {/* Subheadline */}
          <p className="text-white/80 text-lg mt-6 leading-relaxed max-w-md" data-pebble-id="pb-da3450">
            From custom hardscapes to weekly lawn maintenance, Cedar & Stone delivers thoughtful, lasting results — backed by a workmanship warranty and a free design consultation.
          </p>

          {/* CTA row */}
          <div className="mt-10 flex flex-wrap gap-4">
            {/* Primary CTA */}
            <MagneticButton
              href="#contact"
              className="inline-flex items-center justify-center bg-green-700 text-stone-50 px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] hover:opacity-90 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700 focus-visible:ring-offset-2 focus-visible:ring-offset-transparent"
            >
              Get a Free Consultation
            </MagneticButton>

            {/* Tap-to-call — phone CTA */}
            <a
              href="tel:(919) 555-0182"
              className="inline-flex items-center justify-center gap-2 bg-white/10 text-white px-7 py-3 rounded-md font-semibold text-sm tracking-wide min-h-[44px] border border-white/30 hover:bg-white/20 transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-transparent" data-pebble-id="pb-f047a5">
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
              (919) 555-0182
            </a>
          </div>

          {/* Trust strip */}
          <div className="mt-8 pt-6 border-t border-white/20">
            <p className="text-stone-100 text-xs font-medium uppercase tracking-widest" data-pebble-id="pb-91f811">
              Licensed · Insured · Workmanship Warranty
            </p>
          </div>

        </div>
      </div>
    </section>
  );
}
