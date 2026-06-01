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
                  alt="A Portland Plumbing Team That Shows Up and Gets It Done"
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
            <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-5" data-pebble-id="pb-8a59a0">
              Oregon Licensed & Insured · Family-Run
            </p>
            <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight mb-8 max-w-sm" data-pebble-id="pb-56d14c">
              <RevealWords>A Portland Plumbing Team That Shows Up and Gets It Done</RevealWords>
            </h2>

            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-43c251">
              Tidewater Plumbing Co. is a family-run operation dispatched out of SE Portland. We serve the metro and inner suburbs — from Beaverton to Gresham, Lake Oswego to St. Johns.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-5fa623">
              Every technician we send is licensed and trained to handle residential and light commercial plumbing. We give you a flat rate before we start — no hourly billing, no surprise invoices when the job takes longer than expected.
            </p>
            
            <p className="text-slate-600 text-base leading-relaxed mb-5" data-pebble-id="pb-a4a402">
              Most calls get same-day service. We keep our trucks stocked so we're not leaving you waiting on a part. When you call Tidewater, you're talking to someone who works here, not a call center.
            </p>
            

            {/* Signature / credentials line */}
            <div className="mt-8 pt-6 border-t border-slate-200">
              <p className="text-slate-900 text-sm font-semibold tracking-wide" data-pebble-id="pb-c76a79">
                The Tidewater Plumbing Team · SE Portland, OR
              </p>
            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
