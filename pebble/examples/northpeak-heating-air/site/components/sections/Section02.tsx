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
          <p className="text-sky-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-a20e88">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-d13d08">
            <RevealWords>Full-Range HVAC Services for Colorado Homes</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/7347538/pexels-photo-7347538.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="AC Installation & Repair"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-be6368">
                AC Installation & Repair
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-0f76c9">
                Stay cool through Denver's summer swings. We install and repair all major AC systems with flat-rate, upfront pricing.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-4fbaa8">
                from $89
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-ee2a0b">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/7859953/pexels-photo-7859953.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Furnace Replacement & Tune-Ups"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-661b74">
                Furnace Replacement & Tune-Ups
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-eab161">
                Keep your furnace running efficiently through Colorado's harshest winters. We handle replacements and precision tune-ups.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-43a963">
                from $89
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-ec3032">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/20046693/pexels-photo-20046693.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Heat Pumps"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-d6eb6f">
                Heat Pumps
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-59b81c">
                Year-round efficiency for Colorado's climate swings. We size, install, and service heat pump systems for reliable comfort.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-6173ff">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-d60b18">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/32737485/pexels-photo-32737485.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Indoor Air Quality"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-f1ae95">
                Indoor Air Quality
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-fe35a5">
                Professional air quality testing and filtration solutions that remove pollutants and allergens at altitude.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-a422c4">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-caa7a8">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5463581/pexels-photo-5463581.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="24/7 Emergency HVAC"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-871b8e">
                24/7 Emergency HVAC
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-100b5e">
                When heat fails at 2 AM in January or AC quits mid-August, our technicians are dispatched fast — day or night.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-cc46e8">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-e73625">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5463575/pexels-photo-5463575.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Maintenance Plans"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-6bbe78">
                Maintenance Plans
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-99204b">
                Year-round comfort starts with scheduled maintenance. Our plans keep systems tuned and breakdowns off the calendar.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-0dc32b">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-a26773">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
