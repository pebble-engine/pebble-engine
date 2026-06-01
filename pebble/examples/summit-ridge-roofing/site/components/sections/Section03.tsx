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
                  src="https://images.pexels.com/photos/33404080/pexels-photo-33404080.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Summit Ridge Roofing — Straight Talk, Solid Work"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-558a19">
              Licensed · Insured · Manufacturer Certified
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-041c5d">
              <RevealWords>Summit Ridge Roofing — Straight Talk, Solid Work</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-0344da">
              Summit Ridge Roofing is a licensed and insured roofing contractor based in Kansas City, MO. We specialize in residential roof replacement, storm damage repair, and insurance claim navigation for homeowners across the metro area.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-95eb77">
              We hold certifications from major shingle manufacturers, which means the products we install qualify for extended warranty coverage. Every estimate is written, itemized, and delivered before a single nail is driven.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-9e174f">
              When a storm rolls through, we show up fast — free inspections, honest assessments, and direct coordination with your insurance adjuster. No runaround, no surprise invoices.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-e491d5">
                Summit Ridge Roofing · Licensed Roofing Contractor, Kansas City MO
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
