"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-amber-700 text-xs font-semibold uppercase tracking-[0.2em] mb-4" data-pebble-id="pb-a20fe3">
            What We Build
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight tracking-tight" data-pebble-id="pb-f36d4b">
            <RevealWords>Full-Service Remodeling & Construction in Boise</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/3935338/pexels-photo-3935338.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole-Home Remodels"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-687a0d">
                Whole-Home Remodels
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-6cb75e">
                Transform your entire home from top to bottom. We handle every trade in-house or with vetted subs — one team, one fixed price.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/28885519/pexels-photo-28885519.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Room Additions"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-78008c">
                Room Additions
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-0b3e12">
                Need more space? We design and build seamless additions that match your existing home's character and structure.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/10855207/pexels-photo-10855207.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Kitchen Renovations"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-aaa337">
                Kitchen Renovations
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-70bf19">
                Custom cabinetry, updated layouts, and quality finishes that make your kitchen the heart of your home again.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5502225/pexels-photo-5502225.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Bathroom Upgrades"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-5a2682">
                Bathroom Upgrades
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-9f92e9">
                From spa-inspired master baths to efficient guest bathrooms — tile work, fixtures, and everything in between.
              </p>
            </div>
          </StaggerItem>
          
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-stone-50">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/10099330/pexels-photo-10099330.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Custom Decks & Outdoor Living"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-stone-900 text-lg font-semibold leading-snug" data-pebble-id="pb-edc84b">
                Custom Decks & Outdoor Living
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1" data-pebble-id="pb-5a6455">
                Extend your living space outdoors with a custom-built deck, pergola, or covered patio built for Idaho's seasons.
              </p>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
