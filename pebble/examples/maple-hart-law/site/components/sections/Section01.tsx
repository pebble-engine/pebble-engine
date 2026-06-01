"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridClean() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-d53418">
            Areas of practice
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-0d0b50">
            <RevealWords>We handle the legal side so you can focus on your family</RevealWords>
          </h2>
        </div>

        {/* Services grid — 3 columns, text-only cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-c6302a">
              Divorce
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-bd8dc6">
              We guide you through the process step by step — property, finances, and paperwork — and explain every decision in language that actually makes sense.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-983f87">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-a5bd7e">
              Child Custody
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-19a09b">
              Whether you're creating a parenting plan from scratch or modifying an existing one, we help you understand your rights and advocate for your kids.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-b360c7">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-88e37f">
              Adoption
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-f1076b">
              We handle the legal details of bringing a child into your family, including stepparent, private, and agency adoptions, from first filing to final hearing.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-a63eb7">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 p-8 flex flex-col gap-4">
            <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-1da569">
              Free 30-Minute First Call
            </h3>
            <p className="text-slate-500 text-base leading-relaxed flex-1" data-pebble-id="pb-6c7f0d">
              Every new client gets a no-pressure plain English call. We tell you what the process looks like, what to expect, and answer your questions — before you sign anything.
            </p>
            <a
              href="#contact"
              className="text-sky-600 text-sm font-medium tracking-wide hover:text-sky-700 transition mt-2" data-pebble-id="pb-b9ad5b">
              Learn more &rarr;
            </a>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
