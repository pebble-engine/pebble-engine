"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutTeamClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — portrait */}
          <div className="relative">
            <div className="relative aspect-[4/5] overflow-hidden rounded-sm">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/7006668/pexels-photo-7006668.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Gearworks Auto Service — Columbus, OH"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-ad1759">
              ASE-Certified Technicians · Fully Insured Shop
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-0cf045">
              <RevealWords>Gearworks Auto Service — Columbus, OH</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-a70b57">
              Our technicians hold ASE certifications across all major service categories. That means the person working on your vehicle has passed standardized exams in their specialty — not just clocked hours in a bay.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-f28e4c">
              We built our process around transparency. Every vehicle gets a digital inspection with photos attached. You see what we see before you approve a single repair. No surprise line items, no pressure.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-2590be">
              Gearworks carries full shop insurance, stocks loaner cars for customers who can't wait, and offers fleet contracts for local businesses that need reliable scheduled service. We run a professional operation because our customers depend on it.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-20153a">
                Gearworks Auto Service · ASE-Certified · Columbus, OH
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
