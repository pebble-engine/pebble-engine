"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function PricingTiersClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-c4528d">
            Service packages
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight max-w-lg" data-pebble-id="pb-4f808f">
            <RevealWords>Straightforward pricing — no hourly surprises, no hidden fees.</RevealWords>
          </h2>
        </div>

        {/* Tier cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">

          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-2cc363">
                Tax Filing Only
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-6d9ec3">
                  From $350
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-217222">
                  per return
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-591cd8">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-2df5a2">&#10003;</span>
                <span data-pebble-id="pb-b6d7c4">Federal + state individual or business return</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-03f399">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-87859e">&#10003;</span>
                <span data-pebble-id="pb-e337b2">Deduction review included</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-03477e">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-733d3b">&#10003;</span>
                <span data-pebble-id="pb-978276">E-filing and confirmation</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-2f1b86">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-a7f320">&#10003;</span>
                <span data-pebble-id="pb-715ecb">One year of document storage</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-ab6ffe">
              Get started
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-02a751">
                Books + Taxes
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-923e50">
                  From $275
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-b5a33c">
                  / month
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-47a8d7">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-6666b4">&#10003;</span>
                <span data-pebble-id="pb-3cfd06">Monthly bookkeeping & reconciliation</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-ebf030">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-78b458">&#10003;</span>
                <span data-pebble-id="pb-ee53aa">Profit & loss delivered each month</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-a3f820">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-91620c">&#10003;</span>
                <span data-pebble-id="pb-d89f3d">Annual business tax return included</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-e3bcab">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-ac09b9">&#10003;</span>
                <span data-pebble-id="pb-2287c3">IRS notice support included</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-b0472c">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-16b841">&#10003;</span>
                <span data-pebble-id="pb-dcb320">Direct CPA access by phone or email</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-8ef37c">
              Start with a review
            </a>
          </StaggerItem>
          
          <StaggerItem className="relative bg-slate-50 border border-slate-200 rounded-md p-8 flex flex-col gap-6 ring-1 ring-sky-600">
            {/* Tier name + price */}
            <div>
              <span className="text-slate-900 text-xs font-semibold uppercase tracking-[0.15em]" data-pebble-id="pb-0000b5">
                Catch-Up & Clean
              </span>
              <div className="mt-3 flex items-baseline gap-1">
                <span className="text-slate-900 text-4xl font-semibold leading-none tracking-tight" data-pebble-id="pb-1a988e">
                  Custom quote
                </span>
                <span className="text-slate-400 text-sm" data-pebble-id="pb-0be330">
                  one-time
                </span>
              </div>
            </div>

            {/* Divider */}
            <div className="h-px bg-slate-200" aria-hidden="true" />

            {/* Feature list */}
            <ul className="flex-1 space-y-3">
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-ad1d6f">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-24bf01">&#10003;</span>
                <span data-pebble-id="pb-6ae991">Backlog bookkeeping for any period</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-38edde">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-c17095">&#10003;</span>
                <span data-pebble-id="pb-fb8f32">Full reconciliation and gap repair</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-2beac6">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-0dcaa5">&#10003;</span>
                <span data-pebble-id="pb-5fe427">Amended or late returns if needed</span>
              </li>
              
              <li className="flex items-start gap-3 text-slate-600 text-sm leading-relaxed" data-pebble-id="pb-6b9b5b">
                <span className="mt-0.5 text-sky-600 font-semibold leading-none" aria-hidden="true" data-pebble-id="pb-6281a6">&#10003;</span>
                <span data-pebble-id="pb-028576">Handoff to ongoing plan at completion</span>
              </li>
              
            </ul>

            {/* CTA */}
            <a
              href="#contact"
              className="mt-2 bg-sky-600 text-white px-6 py-3 rounded-md font-medium text-sm text-center hover:bg-sky-700 transition tracking-wide" data-pebble-id="pb-4b49d2">
              Book a free review
            </a>
          </StaggerItem>
          

        </Stagger>
      </div>
    </section>
  );
}
