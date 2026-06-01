"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-3fe337">
            Fee schedule
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-lg" data-pebble-id="pb-3ff222">
            <RevealWords>Straightforward fees — no surprises, no hidden costs</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-695209">
                Free First Call
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-70848f">
                  $0
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-fdaa0a">
                  30 minutes
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-41e0fe">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-c61985">&#10003;</span>
                <span data-pebble-id="pb-26d882">Plain English explanation of your situation</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-8d5d6a">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-9a5c2e">&#10003;</span>
                <span data-pebble-id="pb-7c5c44">Overview of your legal options</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-9d0f78">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-a5bc48">&#10003;</span>
                <span data-pebble-id="pb-ea8599">Honest timeline and process walkthrough</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-61086b">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-7f19de">&#10003;</span>
                <span data-pebble-id="pb-a42ea4">No obligation to retain</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-2e249c">
              Book your free call
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-b6ee49">
                Full Representation
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-a5a77b">
                  Flat fee or hourly
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-e7be15">
                  case basis
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-808245">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-15505e">&#10003;</span>
                <span data-pebble-id="pb-119374">Divorce, custody, or adoption handled end-to-end</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-c39bfc">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-318d02">&#10003;</span>
                <span data-pebble-id="pb-343a8b">All filings, negotiations, and court appearances</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-0302aa">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-4c4799">&#10003;</span>
                <span data-pebble-id="pb-5db7df">Clear fee structure agreed before work begins</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-e4874f">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-e3e546">&#10003;</span>
                <span data-pebble-id="pb-d31926">Regular plain-language case updates</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-11c5aa">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-ef9d1f">&#10003;</span>
                <span data-pebble-id="pb-730063">Available for questions throughout</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-978c9d">
              Schedule a consultation
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-6fdab6">
                Unbundled Services
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-c5b04e">
                  From $150
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-50a8bb">
                  per task
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-43525e">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-76fe27">&#10003;</span>
                <span data-pebble-id="pb-70c0d4">Document review and plain-language summary</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-c8143b">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-b67f4e">&#10003;</span>
                <span data-pebble-id="pb-19202d">Coaching for self-represented clients</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-818ea8">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-d16c40">&#10003;</span>
                <span data-pebble-id="pb-751439">Single-session legal advice</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-692ad7">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-214822">&#10003;</span>
                <span data-pebble-id="pb-6327c2">Parenting plan drafting</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-1ee185">
              Ask about this option
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
