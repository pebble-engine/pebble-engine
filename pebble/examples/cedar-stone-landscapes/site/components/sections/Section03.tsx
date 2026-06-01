"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryBeforeafterTrade() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-green-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-2bbf21">
            Recent Work
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-63d0db">
            <RevealWords>Outdoor Spaces Transformed Across the Triangle</RevealWords>
          </h2>
        </div>

        {/* Project grid */}
        <Stagger className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/19740269/pexels-photo-19740269.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Bluestone patio with built-in retaining wall"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-93c17d">Bluestone patio with built-in retaining wall</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/8189102/pexels-photo-8189102.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Native plant garden design installation"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-eaf814">Native plant garden design installation</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/37720375/pexels-photo-37720375.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Custom irrigation system for residential lawn"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-204f55">Custom irrigation system for residential lawn</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/7782975/pexels-photo-7782975.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Seasonal mulching and bed edging refresh"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-c24878">Seasonal mulching and bed edging refresh</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/12763046/pexels-photo-12763046.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Tiered retaining wall with ornamental plantings"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-c05d88">Tiered retaining wall with ornamental plantings</p>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
