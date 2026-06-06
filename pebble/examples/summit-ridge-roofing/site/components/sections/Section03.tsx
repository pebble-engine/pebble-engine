"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryShowcase() {
  return (
    <section className="bg-slate-50 py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-sky-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-5cc8df">
            Recent Projects
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-daa78d">
            <RevealWords>Work We Stand Behind</RevealWords>
          </h2>
        </div>

        {/* Showcase grid — first tile spans 2 cols for visual rhythm */}
        <Stagger className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-[180px] md:auto-rows-[220px] [&>*:first-child]:col-span-2 [&>*:first-child]:row-span-2">
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/4044784/pexels-photo-4044784.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Full replacement — Overland Park, KS"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-a97347">Full replacement — Overland Park, KS</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/11953905/pexels-photo-11953905.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Storm repair — Kansas City, MO"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-fff306">Storm repair — Kansas City, MO</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/10517936/pexels-photo-10517936.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Gutter install — Lee's Summit, MO"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-dd7ccb">Gutter install — Lee's Summit, MO</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/33404080/pexels-photo-33404080.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Post-hail re-roof — Independence, MO"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-8a2ea4">Post-hail re-roof — Independence, MO</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/33404981/pexels-photo-33404981.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Insurance claim job — Raytown, MO"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-bb44d6">Insurance claim job — Raytown, MO</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/31762405/pexels-photo-31762405.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Inspection report — Shawnee, KS"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-b7e0ca">Inspection report — Shawnee, KS</p>
              </div>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
