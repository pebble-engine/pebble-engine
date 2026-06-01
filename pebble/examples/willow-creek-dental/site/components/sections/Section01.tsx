"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-60abeb">
            What we offer
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-315ab2">
            <RevealWords>Care for every stage of life, all under one roof</RevealWords>
          </h2>
        </div>

        {/* Services grid — 3 columns, text-only cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-4bbe76">
              Children's Dentistry
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-c16018">
              Gentle first visits for toddlers through teens. We take the time to make young patients feel safe and curious — not scared.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-4a367f">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-9f13c2">
              Routine Cleanings & Exams
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-ee5091">
              Thorough cleanings with no rushing. We talk through what we find and answer every question before we do anything.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-8fc9fd">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-a74924">
              Restorative Care
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-cadecd">
              Fillings, crowns, and tooth repair done at a pace that feels manageable. We walk you through each step as we go.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-a5f121">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-8edf7e">
              Cosmetic Dentistry
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-451317">
              Whitening, veneers, and smile refinements for patients who want to feel confident — without pressure or upselling.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-4ac827">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-fd934a">
              Senior Dental Care
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-5e320b">
              Attentive care for older patients with longer appointments, clear explanations, and treatments tailored to changing needs.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-63678d">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-c6c48c">
              Anxiety-Friendly Visits
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-66695f">
              Designed for nervous patients. We never rush, always explain, and you can pause any time. Many anxious patients become regulars.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-98218d">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
