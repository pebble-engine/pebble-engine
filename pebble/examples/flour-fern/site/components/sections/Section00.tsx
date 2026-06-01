"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden">
      <div className="absolute inset-0">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="https://images.pexels.com/photos/6794615/pexels-photo-6794615.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Baked slow. Ready by morning."
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        <div className="absolute inset-0 bg-gradient-to-t from-stone-50 via-stone-50/40 to-transparent" />
      </div>
      <div className="relative z-10 container mx-auto px-8 pb-24">
        <p className="text-amber-700 text-sm uppercase tracking-widest mb-4" data-pebble-id="pb-6f336a">
          Small-batch sourdough · Riverside
        </p>
        <h1 className="text-stone-900 text-6xl md:text-8xl font-bold leading-none max-w-4xl" data-pebble-id="pb-e642f7">
          <RevealWords>Baked slow. Ready by morning.</RevealWords>
        </h1>
        <p className="text-stone-900/80 text-xl mt-6 max-w-2xl leading-relaxed" data-pebble-id="pb-d912c1">
          We mix everything by hand, let our doughs ferment for two full days, and pull about 40 loaves each morning. The crust crackles. The crumb pulls apart in ribbons. Come early — we sell out by noon.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <MagneticButton href="#order"
             className="inline-block bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-semibold hover:opacity-90 transition">
            Find us this week
          </MagneticButton>
          <a href="#about"
             className="text-stone-900 px-8 py-4 rounded-full border border-stone-900/30 hover:bg-stone-900/10 transition" data-pebble-id="pb-39e0bc">
            Our story
          </a>
        </div>
      </div>
    </section>
  );
}
