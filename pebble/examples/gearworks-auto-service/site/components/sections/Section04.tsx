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
          <p className="text-red-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-5db767">
            Our Work
          </p>
          <h2 className="text-slate-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-fca6fb">
            <RevealWords>Shop in Action</RevealWords>
          </h2>
        </div>

        {/* Showcase grid — first tile spans 2 cols for visual rhythm */}
        <Stagger className="grid grid-cols-2 md:grid-cols-3 gap-4 auto-rows-[180px] md:auto-rows-[220px] [&>*:first-child]:col-span-2 [&>*:first-child]:row-span-2">
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/34277923/pexels-photo-34277923.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Brake overhaul on a high-mileage sedan"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-7d9ad8">Brake overhaul on a high-mileage sedan</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/4116172/pexels-photo-4116172.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Computerized engine fault diagnosis"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-04f174">Computerized engine fault diagnosis</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8986137/pexels-photo-8986137.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Full tire mount and alignment"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-7849f2">Full tire mount and alignment</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/8478259/pexels-photo-8478259.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="AC condenser replacement"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-331575">AC condenser replacement</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/12700835/pexels-photo-12700835.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Fleet van preventive maintenance"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-a0f208">Fleet van preventive maintenance</p>
              </div>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="relative h-full overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="https://images.pexels.com/photos/4756887/pexels-photo-4756887.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Clean shop, organized bays"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug" data-pebble-id="pb-bf000f">Clean shop, organized bays</p>
              </div>
            </div>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
