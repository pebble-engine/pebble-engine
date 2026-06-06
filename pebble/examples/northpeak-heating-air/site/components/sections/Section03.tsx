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
                  src="https://images.pexels.com/photos/32845660/pexels-photo-32845660.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Northpeak Heating & Air — Straight Talk, Solid Work"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-b5ab30">
              NATE-Certified · Licensed & Insured · Denver, CO
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-24a012">
              <RevealWords>Northpeak Heating & Air — Straight Talk, Solid Work</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-20c0eb">
              Northpeak is a Denver-based HVAC company built around one principle: give customers an honest diagnosis and a fair, flat-rate price — no upsells, no runaround. Our technicians are NATE-certified and carry full licensing and insurance.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-76ba44">
              Colorado's climate demands more from heating and cooling systems than most. Bitter winters, dry summers, and rapid temperature swings mean equipment works harder here. We spec and service systems with that reality in mind, not just the manufacturer's baseline.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-ddfab4">
              Every service call comes with upfront pricing before work begins. Maintenance plan members get priority scheduling and year-round coverage so their systems are ready when the weather turns — and in Colorado, it always does.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-4cd9d5">
                Northpeak Heating & Air · Denver, CO · Licensed & Insured
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
