"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroStrike() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-zinc-900">
      {/* Full-bleed action image */}
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="https://images.pexels.com/photos/7862508/pexels-photo-7862508.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="THE STATIC HITS DIFFERENT."
            fill
            priority
            className="object-cover object-center"
          />
        </Parallax>
        {/* Dark gradient — left side stays readable, right side bleeds raw */}
        <div className="absolute inset-0 bg-gradient-to-r from-zinc-900/95 via-zinc-900/70 to-transparent" />
      </div>

      <div className="relative z-10 container mx-auto px-8 py-24 max-w-6xl">
        {/* Eyebrow — tight caps, wide tracking, lime accent */}
        <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-6" data-pebble-id="pb-b0febf">
          VALORANT. ROCKET LEAGUE. NO LIMITS.
        </p>

        {/* Oversized headline — confrontational scale */}
        <h1 className="text-zinc-50 text-7xl md:text-9xl font-black leading-none uppercase max-w-3xl" data-pebble-id="pb-fd1b11">
          <RevealWords>THE STATIC HITS DIFFERENT.</RevealWords>
        </h1>

        <p className="text-zinc-50/70 text-lg md:text-xl mt-8 max-w-xl leading-snug font-medium" data-pebble-id="pb-0c4111">
          We are Static Vanguard. Grassroots built, arena ready. Two rosters. One identity. The glitch is the signal — and the crowd already knows it.
        </p>

        <div className="mt-12 flex flex-wrap gap-4 items-center">
          <MagneticButton
            href="#start"
            className="inline-block bg-lime-400 text-zinc-900 px-10 py-4 rounded-md font-black uppercase tracking-widest text-sm hover:scale-105 hover:bg-zinc-50 hover:text-zinc-900 transition-all duration-150"
          >
            SEE THE ROSTER
          </MagneticButton>
          <a
            href="#learn"
            className="text-zinc-50 px-10 py-4 rounded-md border-2 border-zinc-50/40 font-bold uppercase tracking-widest text-sm hover:border-lime-400 hover:text-lime-400 transition-all duration-150" data-pebble-id="pb-d3363a">
            PARTNER WITH US
          </a>
        </div>
      </div>
    </section>
  );
}
