"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroStrike() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-{{bg}}">
      {/* Full-bleed action image */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="{{hero_image}}"
            alt="{{headline}}"
            fill
            priority
            className="object-cover object-center"
          />
        </Parallax>
        {/* Dark gradient — left side stays readable, right side bleeds raw */}
        <div className="absolute inset-0 bg-gradient-to-r from-{{bg}}/95 via-{{bg}}/70 to-transparent" />
      </div>

      <div className="relative z-10 container mx-auto px-8 py-24 max-w-6xl">
        {/* Eyebrow — tight caps, wide tracking, lime accent */}
        <p className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em] mb-6">
          {{eyebrow}}
        </p>

        {/* Oversized headline — confrontational scale */}
        <h1 className="text-{{fg}} text-7xl md:text-9xl font-black leading-none uppercase max-w-3xl">
          <RevealWords>{{headline}}</RevealWords>
        </h1>

        <p className="text-{{fg}}/70 text-lg md:text-xl mt-8 max-w-xl leading-snug font-medium">
          {{subheadline}}
        </p>

        <div className="mt-12 flex flex-wrap gap-4 items-center">
          <MagneticButton
            href="#start"
            className="inline-block bg-{{accent}} text-{{bg}} px-10 py-4 rounded-md font-black uppercase tracking-widest text-sm hover:scale-105 hover:bg-{{fg}} hover:text-{{bg}} transition-all duration-150"
          >
            {{cta_primary}}
          </MagneticButton>
          <a
            href="#learn"
            className="text-{{fg}} px-10 py-4 rounded-md border-2 border-{{fg}}/40 font-bold uppercase tracking-widest text-sm hover:border-{{accent}} hover:text-{{accent}} transition-all duration-150"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
