"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-65552b">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-301c46">
            <RevealWords>Electrical Services for Austin Homes & Properties</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-36f268">
              Electrical Panel Upgrades
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-0b6d11">
              Safely upgrade aging or undersized panels to meet modern load demands. Permit-pulled and code-compliant in all Travis County jurisdictions.
            </p>
            <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-8ab1a6">
              
            </span>
            <a
              href="#contact"
              className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-87611f">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-fd457d">
              EV Charger Installation
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-614944">
              Level 2 home charging station installation for all major EV brands. Dedicated circuits sized correctly for your vehicle and panel.
            </p>
            <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-1ab0b5">
              
            </span>
            <a
              href="#contact"
              className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-6e70cf">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-ee5698">
              Indoor & Outdoor Lighting
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-64f2e1">
              Recessed lighting, landscape fixtures, security lighting, and full design-to-install service for interior and exterior spaces.
            </p>
            <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-8232b7">
              
            </span>
            <a
              href="#contact"
              className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-199ba9">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-cb421b">
              Circuit Troubleshooting
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-365497">
              Systematic diagnosis of tripped breakers, flickering lights, dead outlets, and unexplained outages — same-day visits available.
            </p>
            <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-5f2157">
              
            </span>
            <a
              href="#contact"
              className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-af49d9">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-9555b3">
              Whole-Home Generators
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-733e2a">
              Standby generator installation with automatic transfer switches. Keep your home powered through Texas storms and grid outages.
            </p>
            <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-b678f1">
              
            </span>
            <a
              href="#contact"
              className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-4ce8cb">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
