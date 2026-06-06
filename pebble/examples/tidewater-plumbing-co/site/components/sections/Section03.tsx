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
                  src="https://images.pexels.com/photos/16552851/pexels-photo-16552851.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="A Family-Run Shop That Does the Work Right"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-a36495">
              Oregon Licensed & Insured Plumbing Contractor
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-377c67">
              <RevealWords>A Family-Run Shop That Does the Work Right</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-587268">
              Tidewater Plumbing Co. is a family-run operation dispatched out of SE Portland. We handle residential and light commercial plumbing across the metro and inner suburbs — no job gets handed off to a sub you've never met.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-eec838">
              Every technician we send is licensed and trained on the full range of work: drains, water heaters, leak detection, and full repiping. We arrive prepared, diagnose clearly, and give you a flat-rate price before anything gets touched.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-08fb1f">
              Flat-rate pricing means the quote you get is the number you pay. We think that's just how it should work. No hourly billing, no end-of-job surprises — just straightforward plumbing from people who stand behind it.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-0ba8e4">
                The Tidewater Team · Licensed Plumbers · SE Portland
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
