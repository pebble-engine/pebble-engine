"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-green-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-f7fec0">
            What We Do
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-84a2ff">
            <RevealWords>Full-Service Landscaping for Every Outdoor Need</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-stone-50 p-8 flex flex-col gap-4">
            <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-5c9bc2">
              Landscape Design & Installation
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-352cb0">
              Custom garden and yard plans brought to life — from initial sketch to final planting, tailored to Raleigh's climate and your home's character.
            </p>
            <span className="inline-block self-start bg-green-700/10 text-green-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-6fbefe">
              
            </span>
            <a
              href="#contact"
              className="text-green-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700/50 rounded" data-pebble-id="pb-5794b4">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 p-8 flex flex-col gap-4">
            <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-99b9ba">
              Weekly Lawn Care
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-bc80fb">
              Reliable, recurring maintenance that keeps your lawn healthy and presentable through every season without you lifting a finger.
            </p>
            <span className="inline-block self-start bg-green-700/10 text-green-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-bfcb2d">
              
            </span>
            <a
              href="#contact"
              className="text-green-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700/50 rounded" data-pebble-id="pb-937568">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 p-8 flex flex-col gap-4">
            <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-4d33e8">
              Hardscape Construction
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-e36e25">
              Patios, retaining walls, walkways, and outdoor living spaces built with precision craftsmanship and materials that stand the test of time.
            </p>
            <span className="inline-block self-start bg-green-700/10 text-green-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-d17dc6">
              
            </span>
            <a
              href="#contact"
              className="text-green-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700/50 rounded" data-pebble-id="pb-7a5e07">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 p-8 flex flex-col gap-4">
            <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-3f1698">
              Irrigation Install & Repair
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-7db6d7">
              Smart irrigation systems designed for efficiency — and fast, accurate repairs when existing systems need attention.
            </p>
            <span className="inline-block self-start bg-green-700/10 text-green-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-6c2a06">
              
            </span>
            <a
              href="#contact"
              className="text-green-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700/50 rounded" data-pebble-id="pb-78471f">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-stone-50 p-8 flex flex-col gap-4">
            <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-fed679">
              Seasonal Cleanups & Mulching
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3092a1">
              Spring and fall cleanups, fresh mulch application, and bed edging that refresh your landscape and protect your plantings year-round.
            </p>
            <span className="inline-block self-start bg-green-700/10 text-green-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-602c34">
              
            </span>
            <a
              href="#contact"
              className="text-green-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green-700/50 rounded" data-pebble-id="pb-8abf32">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
