"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-green-800 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-98a3da">
            What We Offer
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-07f4f9">
            <RevealWords>Full-Service Landscaping for Every Season</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/34553671/pexels-photo-34553671.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Landscape Design & Installation"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-71ae9d">
                Landscape Design & Installation
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-162f5a">
                We transform bare yards into curated outdoor living spaces — from concept sketches to the final planted bed.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/6728925/pexels-photo-6728925.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Weekly Lawn Care"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-6dc792">
                Weekly Lawn Care
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-3884a7">
                Consistent, detail-oriented mowing, edging, and turf maintenance that keeps your lawn looking sharp all season long.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/37340278/pexels-photo-37340278.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Hardscape Construction"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-e17118">
                Hardscape Construction
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-0e4943">
                Custom patios, retaining walls, and stone walkways built with precision — beautiful structures that stand the test of time.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/32974053/pexels-photo-32974053.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Irrigation Systems"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-98b2e0">
                Irrigation Systems
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-a04773">
                Expert installation and repair of irrigation systems that protect your investment and keep your landscape thriving efficiently.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5735203/pexels-photo-5735203.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Seasonal Cleanups & Mulching"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-429e10">
                Seasonal Cleanups & Mulching
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-a8fd0f">
                Spring and fall cleanups plus fresh mulching that give your property a polished, well-tended look all year round.
              </p>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
