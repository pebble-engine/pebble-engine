"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroPlate() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden bg-stone-900">
      {/* Full-bleed food photograph */}
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
        {/* Rich warm gradient — bottom-heavy, plus a mid scrim so type stays
            readable even over bright/low-contrast food photos */}
        <div className="absolute inset-0 bg-gradient-to-t from-stone-900 via-stone-900/70 to-transparent" />
      </div>

      {/* Copy block — sits beneath the photo like a menu caption */}
      <div className="relative z-10 container mx-auto px-8 pb-20 md:pb-28 max-w-6xl">
        <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-4 [text-shadow:0_1px_8px_rgba(0,0,0,0.5)]">
          {{eyebrow}}
        </p>
        <h1 className="text-stone-50 font-serif text-5xl md:text-7xl leading-tight max-w-3xl mb-6 [text-shadow:0_2px_16px_rgba(0,0,0,0.55)]">
          <RevealWords>{{headline}}</RevealWords>
        </h1>
        <p className="text-stone-200/80 text-lg md:text-xl font-sans leading-relaxed max-w-2xl mb-10 [text-shadow:0_1px_10px_rgba(0,0,0,0.5)]">
          {{subheadline}}
        </p>
        <div className="flex flex-wrap gap-4">
          <MagneticButton
            href="#reserve"
            className="inline-block bg-{{accent}} text-{{accent_fg}} px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200"
          >
            {{cta_primary}}
          </MagneticButton>
          <a
            href="#menu"
            className="text-stone-100 px-8 py-4 rounded-full border border-stone-400/40 font-sans hover:bg-stone-50/10 transition"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
