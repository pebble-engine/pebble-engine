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
            src="https://images.pexels.com/photos/10773643/pexels-photo-10773643.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
            alt="Your hair, remembered — every single time."
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        <div className="absolute inset-0 bg-gradient-to-t from-stone-50 via-stone-50/40 to-transparent" />
      </div>
      <div className="relative z-10 container mx-auto px-8 pb-24">
        <p className="text-amber-700 text-sm uppercase tracking-widest mb-4" data-pebble-id="pb-7247b9">
          A little salon on the east side
        </p>
        <h1 className="text-stone-900 text-6xl md:text-8xl font-bold leading-none max-w-4xl" data-pebble-id="pb-1875a5">
          <RevealWords>Your hair, remembered — every single time.</RevealWords>
        </h1>
        <p className="text-stone-900/80 text-xl mt-6 max-w-2xl leading-relaxed" data-pebble-id="pb-07ff76">
          We're a converted house with three chairs, a kettle always on, and stylists who know your name, your last cut, and exactly how you like your tea.
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <MagneticButton href="#order"
             className="inline-block bg-amber-700 text-stone-50 px-8 py-4 rounded-full font-semibold hover:opacity-90 transition">
            Book an appointment
          </MagneticButton>
          <a href="#about"
             className="text-stone-900 px-8 py-4 rounded-full border border-stone-900/30 hover:bg-stone-900/10 transition" data-pebble-id="pb-cfcd05">
            Our story
          </a>
        </div>
      </div>
    </section>
  );
}
