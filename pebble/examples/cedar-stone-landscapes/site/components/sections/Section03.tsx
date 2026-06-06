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
          <p className="text-green-800 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-7e8e5a">
            Recent Projects
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-3511fd">
            <RevealWords>Our Work in the Triangle</RevealWords>
          </h2>
        </div>

        {/* Showcase grid — first tile spans 2 cols for visual rhythm */}
        <Stagger className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-[180px] md:auto-rows-[220px] [&>*:first-child]:col-span-2 [&>*:first-child]:row-span-2">
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/13048511/pexels-photo-13048511.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Bluestone patio with built-in seating wall"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-b95c17">Bluestone patio with built-in seating wall</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/29172233/pexels-photo-29172233.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Native plant garden bed installation"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-883fe5">Native plant garden bed installation</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/35961120/pexels-photo-35961120.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Tiered retaining wall on sloped lot"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-604763">Tiered retaining wall on sloped lot</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/11654274/pexels-photo-11654274.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Full lawn renovation, Cary NC"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-9c8cc3">Full lawn renovation, Cary NC</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/10606633/pexels-photo-10606633.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Drip irrigation system for garden beds"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-cb96a1">Drip irrigation system for garden beds</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/5807154/pexels-photo-5807154.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Spring cleanup and fresh mulch application"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-c38f53">Spring cleanup and fresh mulch application</p>
              </div>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
