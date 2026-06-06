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
                  src="https://images.pexels.com/photos/29491360/pexels-photo-29491360.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Brightwire Electric — Built on Safe, Code-Compliant Work"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-3bd6e3">
              Licensed Master Electrician · Travis County
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-5fd3bb">
              <RevealWords>Brightwire Electric — Built on Safe, Code-Compliant Work</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-e2bd6d">
              Brightwire Electric is a licensed master electrician operation based in Austin, TX. Every job — from a single circuit repair to a full panel replacement — is handled to code and permitted for every jurisdiction in Travis County.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-333ccf">
              We specialize in the work that matters most to Austin homeowners: panel upgrades for aging infrastructure, EV charger installs as the city grows, and whole-home generators for Texas storm season. No subcontractors, no shortcuts.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-30dffa">
              Safety-first isn't a slogan here — it shapes how we diagnose, plan, and execute every project. You receive a written estimate before we touch anything, so there are no surprises when the job is done.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-4bca11">
                Brightwire Electric · Licensed Master Electrician · Austin, TX
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
