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
                  src="https://images.pexels.com/photos/8872600/pexels-photo-8872600.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="We built Maple & Ledger for the business owners the big firms ignore."
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-b4013d">
              Licensed CPA · Local since 2011
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-bda103">
              <RevealWords>We built Maple & Ledger for the business owners the big firms ignore.</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-9a5ca5">
              Maple & Ledger started because too many local business owners were getting burned — by accountants who disappeared after April, by software that confused more than it helped, and by IRS notices nobody explained to them.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-af253d">
              We work exclusively with small businesses and individuals. Restaurants, contractors, salons, solo operators — the kind of clients who need someone who actually knows their name and answers the phone when something comes up.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-d11276">
              Our team is small by choice. Every client works directly with a licensed CPA, not a rotating cast of junior staff. That means consistent work, honest advice, and no surprises at year-end.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-a842a6">
                Maple & Ledger CPA · Licensed & Local
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
