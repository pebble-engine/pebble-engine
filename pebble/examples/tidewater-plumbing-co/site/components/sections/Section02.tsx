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
          <p className="text-sky-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-261a70">
            What We Do
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight max-w-xl tracking-tight" data-pebble-id="pb-c28a10">
            <RevealWords>Plumbing Services for Portland Homes & Businesses</RevealWords>
          </h2>
        </div>

        {/* Services grid — photo-top cards */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-px bg-slate-200">
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/29226620/pexels-photo-29226620.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Drain Cleaning"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-530d6a">
                Drain Cleaning
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-883eef">
                Slow or completely blocked drain? We clear clogs fast and leave your pipes flowing like they should — no mess, no guesswork.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-eb1dd4">
                from $89
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-4dd257">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/9551366/pexels-photo-9551366.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Water Heater Install & Repair"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-5fb8fb">
                Water Heater Install & Repair
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-bfc5ab">
                Cold showers are not optional. We install and repair tank and tankless water heaters quickly, with parts that last.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-900976">
                from $149
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-e484a9">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/34295406/pexels-photo-34295406.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Leak Detection"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-15173b">
                Leak Detection
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-fabafc">
                A hidden leak can do serious damage before you ever see it. We locate the source accurately and stop it before costs compound.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-403aad">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-b1955c">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/28169591/pexels-photo-28169591.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Repiping"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-17145a">
                Repiping
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-bce4c9">
                Old galvanized or corroded pipes dragging down your water pressure? We repipe homes with modern materials built for the long haul.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-c25887">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-8fa8f0">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
          <StaggerItem className="bg-slate-50 flex flex-col overflow-hidden">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/16509869/pexels-photo-16509869.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="24/7 Emergency Calls"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-8 flex flex-col gap-4 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-65e37b">
                24/7 Emergency Calls
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-7a2360">
                Burst pipe at midnight? Flooding on a Sunday? Call us any hour. We dispatch from SE Portland and get there fast when it matters most.
              </p>
              <span className="inline-block self-start bg-sky-700/10 text-sky-700 text-xs font-semibold uppercase tracking-wide px-2.5 py-1 rounded" data-pebble-id="pb-0ab40d">
                
              </span>
              <a
                href="#contact"
                className="text-sky-700 text-sm font-semibold tracking-wide hover:opacity-75 transition-opacity mt-2 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky-700/50 rounded" data-pebble-id="pb-2b6a64">
                Request a quote &rarr;
              </a>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
