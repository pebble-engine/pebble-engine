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
                  src="https://images.pexels.com/photos/6196677/pexels-photo-6196677.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="The Sparrow Team: Detail-Obsessed Cleaners You Can Trust"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-f5794e">
              Fully Insured, Bonded & Background-Checked
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-425b4b">
              <RevealWords>The Sparrow Team: Detail-Obsessed Cleaners You Can Trust</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-514df4">
              Every Sparrow team member is thoroughly background-checked, insured, and trained to our detailed cleaning standards before ever entering a client's home. We don't cut corners — on vetting or on cleaning.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-30f720">
              We assign consistent teams to each home so you always have familiar, trusted faces. Your preferences are remembered, your routines respected, and your space treated with care on every single visit.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-e441f9">
              For clients who prefer it, we offer eco-friendly cleaning products that are effective, safe for kids and pets, and gentle on the environment — just let us know when you book.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-96c57d">
                The Sparrow Home Cleaning Team · Minneapolis, MN
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
