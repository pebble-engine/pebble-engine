"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-slate-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-red-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-532750">
            What We Offer
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-e90199">
            <RevealWords>Full-Service Auto Repair for Columbus Drivers</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/12271951/pexels-photo-12271951.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Computerized Diagnostics"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-8c46f1">
                Computerized Diagnostics
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-781d59">
                We scan your vehicle's computer, pinpoint the actual fault, and explain it in plain language — no guesswork, no unnecessary repairs.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/6870299/pexels-photo-6870299.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Brake Service"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-96c5f4">
                Brake Service
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-9af61d">
                Pads, rotors, calipers, and hydraulics — we inspect every component and restore full stopping power safely and efficiently.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8985606/pexels-photo-8985606.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Oil & Filter Changes"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-ca0e89">
                Oil & Filter Changes
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-c10248">
                Quick, clean, and done right. We use the oil grade your manufacturer specifies and check key fluids every time.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8985662/pexels-photo-8985662.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="AC Recharge & Repair"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-1a5b5d">
                AC Recharge & Repair
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-0349ec">
                We diagnose leaks, replace failed components, and recharge your system so you stay cool all summer long.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/3806288/pexels-photo-3806288.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Tire Sales & Alignment"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-645e65">
                Tire Sales & Alignment
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-4389ac">
                We carry quality tires for every budget and use precision alignment equipment to extend tread life and keep you on course.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-slate-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/7019372/pexels-photo-7019372.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Fleet Maintenance Contracts"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-slate-900 text-lg font-semibold leading-snug" data-pebble-id="pb-579619">
                Fleet Maintenance Contracts
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-c61152">
                Keep your commercial vehicles on the road with scheduled maintenance plans built around your fleet's specific needs.
              </p>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
