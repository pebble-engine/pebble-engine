"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function GalleryShowcase() {
  return (
    <section className="bg-{{bg}} py-20 md:py-28">
      <div className="max-w-7xl mx-auto px-4 md:px-6">
        {/* Section header */}
        <div className="mb-12 max-w-2xl">
          <p className="text-{{accent}} text-sm uppercase tracking-widest mb-3">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Showcase grid — first tile spans 2 cols for visual rhythm */}
        <Stagger className="grid grid-cols-2 md:grid-cols-3 gap-4 [&>*:first-child]:col-span-2 [&>*:first-child]:row-span-2">
          {/* {{projects_list_start}} */}
          <StaggerItem className="group">
            <div className="relative aspect-[4/3] overflow-hidden rounded-lg bg-slate-100">
              <Image
                src="{{projects[].image}}"
                alt="{{projects[].caption}}"
                fill
                sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-700 group-hover:scale-105"
              />
              <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black/60 to-transparent p-3 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <p className="text-white text-sm leading-snug">{{projects[].caption}}</p>
              </div>
            </div>
          </StaggerItem>
          {/* {{projects_list_end}} */}
        </Stagger>
      </div>
    </section>
  );
}
