"use client";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryBeforeafterTrade() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="max-w-6xl mx-auto">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Project grid */}
        <Stagger className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* {{projects_list_start}} */}
          <StaggerItem className="group">
            <div className="aspect-[4/3] overflow-hidden rounded-md bg-slate-100">
              <img
                src="{{projects[].image}}"
                alt="{{projects[].caption}}"
                loading="lazy"
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            <p className="mt-3 text-sm text-slate-600">{{projects[].caption}}</p>
          </StaggerItem>
          {/* {{projects_list_end}} */}
        </Stagger>
      </div>
    </section>
  );
}
