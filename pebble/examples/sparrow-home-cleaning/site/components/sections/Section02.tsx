"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-sky-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-0b5257">
            Our Services
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-787e8a">
            <RevealWords>Cleaning Solutions for Every Home & Office</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-sky-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/6195277/pexels-photo-6195277.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Recurring Weekly Cleaning"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-0f2548">
                Recurring Weekly Cleaning
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-14d7ca">
                Consistent, thorough cleaning on your schedule with the same trusted team assigned to your home every visit.
              </p>
              <span className="inline-block self-start bg-sky-600/10 text-sky-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-0a0d13">
                From $120
              </span>
              <a
                href="#contact"
                className="text-sky-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600/50 rounded" data-pebble-id="pb-545e40">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/13009887/pexels-photo-13009887.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Biweekly Home Cleaning"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-ade994">
                Biweekly Home Cleaning
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-2c5638">
                Stay on top of household upkeep with a reliable biweekly visit — fresh, detailed cleaning every other week.
              </p>
              <span className="inline-block self-start bg-sky-600/10 text-sky-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-062641">
                From $140
              </span>
              <a
                href="#contact"
                className="text-sky-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600/50 rounded" data-pebble-id="pb-d42518">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/4239007/pexels-photo-4239007.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Deep Clean"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-53a2d0">
                Deep Clean
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-d61983">
                A thorough top-to-bottom clean covering baseboards, appliances, grout, and every overlooked corner.
              </p>
              <span className="inline-block self-start bg-sky-600/10 text-sky-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-41692d">
                From $250
              </span>
              <a
                href="#contact"
                className="text-sky-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600/50 rounded" data-pebble-id="pb-2a6cfe">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/36715248/pexels-photo-36715248.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Move-In & Move-Out Clean"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-2933a7">
                Move-In & Move-Out Clean
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-6acb1e">
                Leave your old space spotless or arrive to a fresh start — detailed cleaning tailored for transitions.
              </p>
              <span className="inline-block self-start bg-sky-600/10 text-sky-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-aa27a0">
                From $200
              </span>
              <a
                href="#contact"
                className="text-sky-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600/50 rounded" data-pebble-id="pb-04a4c0">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-sky-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/36175676/pexels-photo-36175676.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Small Office Cleaning"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-8cb6b6">
                Small Office Cleaning
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-7e5ee2">
                Keep your workspace tidy and professional with scheduled cleaning designed for small offices in Minneapolis.
              </p>
              <span className="inline-block self-start bg-sky-600/10 text-sky-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-a6bd40">
                From $130
              </span>
              <a
                href="#contact"
                className="text-sky-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-600/50 rounded" data-pebble-id="pb-364dd7">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
