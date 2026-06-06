"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryShowcase() {
  return (
    <section className="bg-stone-50 py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-a4de7f">
            Recent Projects
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-9e55a8">
            <RevealWords>Our Work Speaks for Itself</RevealWords>
          </h2>
        </div>

        {/* Showcase grid — first tile spans 2 cols for visual rhythm */}
        <Stagger className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-[180px] md:auto-rows-[220px] [&>*:first-child]:col-span-2 [&>*:first-child]:row-span-2">
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/36777912/pexels-photo-36777912.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Open-Concept Kitchen Remodel, Boise"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-e2af76">Open-Concept Kitchen Remodel, Boise</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8583816/pexels-photo-8583816.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Master Suite Addition, Eagle ID"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-9ffbe4">Master Suite Addition, Eagle ID</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/15062122/pexels-photo-15062122.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Spa Bathroom Renovation"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-a92982">Spa Bathroom Renovation</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/13871279/pexels-photo-13871279.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Covered Outdoor Deck, Meridian ID"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-a7205e">Covered Outdoor Deck, Meridian ID</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/15798784/pexels-photo-15798784.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole-Home Remodel, Boise Foothills"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-1c81c4">Whole-Home Remodel, Boise Foothills</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/20705883/pexels-photo-20705883.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Custom Mudroom & Laundry Addition"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-d1efb5">Custom Mudroom & Laundry Addition</p>
              </div>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
