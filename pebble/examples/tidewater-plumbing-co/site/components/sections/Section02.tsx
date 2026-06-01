"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-846190">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-ab7119">
            <RevealWords>Plumbing Services for Portland Homes & Businesses</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-d507d0">
              Drain Cleaning
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-720a65">
              Slow or fully blocked drains cleared fast. We clear kitchen, bath, and main lines and leave your pipes flowing clean.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-bba396">
              From $89
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-07f484">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-57da1b">
              Water Heater Install & Repair
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-1d9b80">
              Hot water out? We install, replace, and repair tank and tankless water heaters with same-day availability on most calls.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-b7153e">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-9790c5">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-4c72a3">
              Leak Detection
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3c5149">
              Hidden leaks found without tearing up your walls. We pinpoint the source, explain the fix, and get it done right.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-119971">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-b09a17">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-56720a">
              Repiping
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-bfbfcc">
              Old, corroded, or failing pipes replaced from end to end. We repipe homes and businesses with minimal disruption.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-82bbc6">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-ae0ec6">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-9f48ec">
              24/7 Emergency Plumbing
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-951b7c">
              Burst pipe at midnight? We answer every call around the clock and dispatch from SE Portland to reach you quickly.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-697bec">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-598f1b">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
