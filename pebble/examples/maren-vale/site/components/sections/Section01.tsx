"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import FadeUp from "@/components/motion/FadeUp";
import Parallax from "@/components/motion/Parallax";

export default function AboutEthos() {
  return (
    <section className="bg-stone-50 py-32 px-8 overflow-hidden">
      <div className="container mx-auto max-w-6xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-20 items-start">

          {/* Left — prose, floated top */}
          <div className="md:pt-8">
            <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-8 font-light" data-pebble-id="pb-54b4a5">
              Our ethos.
            </p>
            <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-[1.1] tracking-tight mb-10 max-w-lg" data-pebble-id="pb-654b18">
              <RevealWords>A quiet studio. A single maker. Every piece, from sketch to metal.</RevealWords>
            </h2>

            <FadeUp>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-3408aa">
              I work alone at my bench — sawing, soldering, setting stones by hand. There is no production line, no factory overseas. Each commission moves at the pace of the work itself, unhurried and considered.
            </p>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-b17bfc">
              Before any metal is touched, I draw. Every client receives an original hand-sketched design on cotton paper — a rendering of the piece made just for them. That sketch is yours to keep, always.
            </p>
            
            <p className="text-stone-500 text-lg font-light leading-relaxed mb-6" data-pebble-id="pb-886a56">
              Most of the people who come to me are marking something: a proposal, an anniversary, a loss, a birth. I hold that weight carefully. The jewelry I make is meant to last generations.
            </p>
            
            </FadeUp>

            {/* Signature — thin rule above */}
            <div className="mt-12 pt-8 border-t border-stone-200">
              <p className="text-stone-600 text-base font-light italic tracking-wide" data-pebble-id="pb-5221e4">
                — Maren, Founder & Goldsmith
              </p>
            </div>
          </div>

          {/* Right — portrait, accent accent block behind it */}
          <div className="relative">
            <div className="relative aspect-[3/4] rounded-2xl overflow-hidden">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/7166987/pexels-photo-7166987.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="A quiet studio. A single maker. Every piece, from sketch to metal."
                  fill
                  priority
                  className="object-cover"
                />
              </Parallax>
              {/* Soft cream gradient at base — doesn't crush the image */}
              <div className="absolute inset-0 bg-gradient-to-t from-stone-50/20 to-transparent" />
            </div>
            {/* Decorative accent square — floated behind */}
            <div className="absolute -bottom-8 -left-8 w-40 h-40 rounded-2xl bg-amber-600/8 -z-10" />
            <div className="absolute -top-4 -right-4 w-24 h-24 rounded-full bg-rose-200/30 -z-10" />
          </div>

        </div>
      </div>
    </section>
  );
}
