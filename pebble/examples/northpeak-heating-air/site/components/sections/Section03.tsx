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
                  src="https://images.pexels.com/photos/36085816/pexels-photo-36085816.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-ec4b5f">
              NATE-Certified · Licensed & Insured · Denver, CO
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-71fbf4">
              <RevealWords>Northpeak Heating & Air — Straight Talk, Solid Work</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-2d558d">
              Northpeak operates on one principle: show up prepared, diagnose accurately, and fix it right the first time. Our NATE-certified technicians carry the training and tools to handle Denver's full range of HVAC demands.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-20cd82">
              Colorado's climate is not average — high altitude, dry winters, and temperature swings that can hit both extremes in a single week. We spec and install equipment that performs at altitude, not just at sea level.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-b7296d">
              Every service call is flat-rate priced before we start. No hidden fees, no upsell pressure. We give you the number, you approve the work, and we get it done. That's the Northpeak standard.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-2239b1">
                Northpeak Heating & Air · Licensed HVAC Contractor · Denver, CO
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
