"use client";

import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryBeforeafterTrade() {
  return (
    <section className="bg-stone-50 py-24 px-8">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-amber-700 text-sm uppercase tracking-widest mb-3" data-pebble-id="pb-5db5ef">
            Recent Projects
          </p>
          <h2 className="text-stone-900 text-4xl md:text-5xl font-semibold leading-tight" data-pebble-id="pb-1ac7d6">
            <RevealWords>Work We're Proud to Put Our Name On</RevealWords>
          </h2>
        </div>

        {/* Project grid */}
        <Stagger className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/36035072/pexels-photo-36035072.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Whole-Home Remodel — North End Boise"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-3c70de">Whole-Home Remodel — North End Boise</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/37357023/pexels-photo-37357023.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Kitchen Renovation — Eagle, ID"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-008a8c">Kitchen Renovation — Eagle, ID</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/10827349/pexels-photo-10827349.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Master Bathroom Upgrade — Meridian"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-8b36c4">Master Bathroom Upgrade — Meridian</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/7546605/pexels-photo-7546605.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Composite Deck Build — Southeast Boise"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-2831bd">Composite Deck Build — Southeast Boise</p>
          </StaggerItem>
          
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="https://images.pexels.com/photos/37627540/pexels-photo-37627540.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Room Addition — Nampa, ID"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600" data-pebble-id="pb-219b45">Room Addition — Nampa, ID</p>
          </StaggerItem>
          
        </Stagger>
      </div>
    </section>
  );
}
