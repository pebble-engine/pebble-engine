"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesPhotoGrid() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-14 max-w-2xl">
          <p className="text-{{accent}} text-xs font-semibold uppercase tracking-[0.2em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-4xl md:text-5xl font-semibold leading-tight tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        <Stagger className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {/* {{services_list_start}} */}
          <StaggerItem className="flex flex-col rounded-2xl overflow-hidden border border-slate-200 bg-{{bg}}">
            <div className="relative aspect-[4/3] overflow-hidden bg-slate-100">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="object-cover transition-transform duration-500 hover:scale-105"
              />
            </div>
            <div className="p-6 flex flex-col gap-3 flex-1">
              <h3 className="text-{{fg}} text-lg font-semibold leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-slate-600 text-base leading-relaxed flex-1">
                {{services[].body}}
              </p>
            </div>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>
      </div>
    </section>
  );
}
