"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutTeamClean() {
  return (
    <section className="bg-sky-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — portrait */}
          <div className="relative">
            <div className="relative aspect-[4/5] overflow-hidden rounded-sm">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/6195125/pexels-photo-6195125.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="The Sparrow Standard: Detail-Obsessed, Every Time"
                  fill
                  priority
                  className="object-cover grayscale-[15%]"
                />
              </Parallax>
            </div>
            {/* Accent rule below portrait */}
            <div className="mt-5 h-px w-16 bg-sky-600" aria-hidden="true" />
          </div>

          {/* Right — credentials + prose */}
          <div className="md:pt-8">
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-a12900">
              Fully Insured, Bonded & Background-Checked
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-975bfb">
              <RevealWords>The Sparrow Standard: Detail-Obsessed, Every Time</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-f132ff">
              Every Sparrow cleaner is background-checked before their first day and trained on our detailed room-by-room checklist. We don't cut corners — literally. Baseboards, ceiling fans, behind appliances: it's all in the routine.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-8faf5b">
              We're fully insured and bonded, so you can hand over your keys with total peace of mind. Eco-friendly cleaning products are available on request at no extra charge — just let us know when you book.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-9332fc">
              You'll be matched with a consistent assigned team so your cleaners know your home, your preferences, and your pets' names. If anything ever falls short, our satisfaction guarantee means we come back and make it right — no hassle, no argument.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-8bcd8b">
                The Sparrow Home Cleaning Team · Minneapolis, MN
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
