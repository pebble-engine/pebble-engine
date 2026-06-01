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
                  alt="Brightwire Electric — Technical Work Done Right"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-5529ba">
              Licensed Master Electrician · Fully Insured
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-a55b44">
              <RevealWords>Brightwire Electric — Technical Work Done Right</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-cd2712">
              Brightwire Electric is a licensed master electrician service based in Austin, TX, built on straightforward trade practices: diagnose accurately, quote honestly, and complete the work to code the first time.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-209db1">
              Every project is permit-ready for all Travis County jurisdictions. Before any work begins, you receive a written estimate in full — no surprise line items, no pressure tactics. Safety compliance is the baseline, not an upsell.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-4cb031">
              From a panel upgrade to a whole-home generator or EV charger circuit, each job is handled with the technical rigor it requires. Same-day diagnostic visits mean you're not waiting days to find out what's wrong.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-d544e8">
                Brightwire Electric · Licensed Master Electrician · Austin, TX
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
