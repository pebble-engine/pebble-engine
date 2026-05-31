"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridBold() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header — left-aligned, dominant */}
        <div className="mb-16">
          <p className="text-{{accent}} text-xs font-black uppercase tracking-[0.3em] mb-4">
            {{eyebrow}}
          </p>
          <h2 className="text-{{fg}} text-6xl md:text-8xl font-black leading-none uppercase max-w-3xl">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services grid — dark cards, lime accent on hover */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* {{services_list_start}} */}
          <StaggerItem className="group relative bg-{{muted}} overflow-hidden rounded-md hover:ring-2 hover:ring-{{accent}} transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-{{accent}} scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-{{fg}} text-xl font-black uppercase leading-tight mb-2 tracking-tight">
                {{services[].title}}
              </h3>
              <p className="text-{{fg}}/60 text-sm leading-snug mb-4">
                {{services[].body}}
              </p>
              <span className="text-{{accent}} text-sm font-black uppercase tracking-widest">
                {{services[].price}}
              </span>
            </div>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
