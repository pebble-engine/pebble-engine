"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroFullbleedEditorial() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden bg-neutral-900">
      {/* Full-bleed image — the photograph speaks; a soft bottom scrim (NOT a
          flat overlay) keeps the light type legible over bright photos. */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="{{hero_image}}"
            alt="{{headline}}"
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-neutral-950/70 via-neutral-950/20 to-transparent" />
      </div>

      {/* Floating type — bottom-left, deliberately small against the frame */}
      <div className="relative z-10 px-8 md:px-16 pb-14 md:pb-20 max-w-2xl">
        <p className="text-neutral-200 text-xs uppercase tracking-widest mb-5 font-sans [text-shadow:0_1px_8px_rgba(0,0,0,0.45)]">
          {{eyebrow}}
        </p>
        <h1 className="font-serif text-neutral-50 text-4xl md:text-6xl leading-tight mb-6 [text-shadow:0_2px_16px_rgba(0,0,0,0.5)]">
          <RevealWords>{{headline}}</RevealWords>
        </h1>
        <p className="text-neutral-300 text-base leading-relaxed mb-8 max-w-sm font-sans">
          {{subheadline}}
        </p>
        <div className="flex flex-wrap gap-6 items-center">
          <MagneticButton
            href="#work"
            className="inline-block text-neutral-50 text-sm tracking-wide border-b border-neutral-50/60 pb-px hover:border-neutral-50 transition-colors"
          >
            {{cta_primary}}
          </MagneticButton>
          <a
            href="#about"
            className="text-neutral-400 text-sm tracking-wide hover:text-neutral-200 transition-colors"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
