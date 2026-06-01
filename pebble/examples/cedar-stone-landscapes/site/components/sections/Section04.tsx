"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";

export default function AboutTeamClean() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">

          {/* Left — portrait */}
          <div className="relative">
            <div className="relative aspect-[4/5] overflow-hidden rounded-sm">
              <Parallax className="absolute inset-0" distance={30}>
                <Image
                  src="https://images.pexels.com/photos/35181295/pexels-photo-35181295.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Cedar & Stone Landscapes — Raleigh, NC"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-a8e1e6">
              Licensed · Insured · Triangle Area Landscapers
            </p>
            <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-db0ad3">
              <RevealWords>Cedar & Stone Landscapes — Raleigh, NC</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-a957ba">
              Cedar & Stone Landscapes is a licensed and insured landscaping company based in Raleigh, NC, serving homeowners and properties across the Triangle. Our work spans design, installation, hardscape construction, and ongoing maintenance.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-b931af">
              Every project begins with a free design consultation — a chance to understand your space, your goals, and the conditions that shape what will actually thrive. We work methodically, with attention to drainage, soil, sun exposure, and long-term plant health.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-ab5562">
              We stand behind every job with a workmanship warranty, because a landscape is an investment. Whether you're building a patio, installing an irrigation system, or simply keeping your lawn in top shape, we deliver work that holds up.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-stone-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-721a98">
                Cedar & Stone Landscapes · Raleigh, NC
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
