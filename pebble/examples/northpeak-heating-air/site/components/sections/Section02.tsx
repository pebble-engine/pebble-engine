"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-5df0a2">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-ad3ec3">
            <RevealWords>Full-Range HVAC Services for Denver Homes & Businesses</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-7fcece">
              AC Installation & Repair
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-ccaa90">
              Stay cool through Colorado summers. We install, service, and repair all major AC brands with same-day availability and flat-rate quotes.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-710d6d">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-3a56f3">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-a36262">
              Furnace Replacement & Tune-Ups
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-cdb978">
              Keep the heat on when temperatures drop. Full furnace replacements and precision tune-ups to maximize efficiency and reliability.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-cf2b40">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-8a352d">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-198e68">
              Heat Pumps
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-e4dd77">
              Year-round efficiency with a single system. We size, install, and maintain heat pumps suited to Denver's altitude and temperature swings.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-95c7c7">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-8909bd">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-d2dfe6">
              Indoor Air Quality
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-052580">
              Professional air quality testing and advanced filtration solutions to remove allergens, dust, and pollutants from your Colorado home.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-0269ae">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-5926a1">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-370c78">
              24/7 Emergency HVAC
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-8a2387">
              When your system fails at midnight in January, we answer. Round-the-clock emergency dispatch with no after-hours surcharge surprises.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-094339">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-6ab60d">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-87c368">
              Maintenance Plans
            </h3>
            <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-a69c7e">
              Year-round comfort starts with planned upkeep. Our maintenance plans cover seasonal inspections, priority scheduling, and member-only rates.
            </p>
            <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-611de4">
              None
            </span>
            <a
              href="#contact"
              className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-50d5e5">
              Request a quote &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
