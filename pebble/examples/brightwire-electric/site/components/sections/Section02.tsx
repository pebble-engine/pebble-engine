"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridTrade() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">

        {/* Section header */}
        <div className="mb-16">
          <p className="text-amber-600 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-2eb9cd">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-947d75">
            <RevealWords>Electrical Services for Austin Homes & Businesses</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/32497160/pexels-photo-32497160.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Electrical Panel Upgrades"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-d598bf">
                Electrical Panel Upgrades
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3e09f1">
                Replace outdated or undersized panels to safely handle modern electrical loads. Permit-ready for all Travis County jurisdictions.
              </p>
              <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-489e17">
                
              </span>
              <a
                href="#contact"
                className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-baece1">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/27355826/pexels-photo-27355826.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="EV Charger Installation"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-2c20c5">
                EV Charger Installation
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-ce34e5">
                Level 2 home charging stations wired and installed correctly, so your vehicle is ready every morning without tripping your panel.
              </p>
              <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-d63516">
                
              </span>
              <a
                href="#contact"
                className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-e9060e">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/4792521/pexels-photo-4792521.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Indoor & Outdoor Lighting Design"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-647ade">
                Indoor & Outdoor Lighting Design
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-dcfafa">
                Recessed lighting, landscape fixtures, and accent lighting planned and installed for both function and curb appeal.
              </p>
              <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-5a4ea7">
                
              </span>
              <a
                href="#contact"
                className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-bd53b6">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/6349399/pexels-photo-6349399.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Circuit Troubleshooting"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-cfa858">
                Circuit Troubleshooting
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-7b052c">
                Pinpoint tripping breakers, flickering lights, or dead outlets fast with same-day diagnostic visits available throughout Austin.
              </p>
              <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-48124b">
                
              </span>
              <a
                href="#contact"
                className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-9f63bc">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/9875678/pexels-photo-9875678.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole-Home Generators"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-441e5d">
                Whole-Home Generators
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-c52796">
                Automatic standby generators sized, installed, and permitted so your home stays powered through any outage — no extension cords required.
              </p>
              <span className="inline-block self-start bg-amber-600/10 text-amber-600 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-daf99f">
                
              </span>
              <a
                href="#contact"
                className="text-amber-600 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-600/50 rounded" data-pebble-id="pb-013e7e">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
