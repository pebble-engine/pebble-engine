"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Sparse header — left-aligned, no centering */}
        <div className="mb-16 border-b border-{{fg}}/10 pb-10">
          <p className="text-{{muted}} text-xs uppercase tracking-widest mb-4 font-sans">
            {{eyebrow}}
          </p>
          <h2 className="font-serif text-{{fg}} text-4xl md:text-5xl leading-tight max-w-xl">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services — two-column editorial grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 gap-px bg-{{fg}}/8">
          {/* {{services_list_start}} */}
          <StaggerItem className="bg-{{bg}} p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-{{fg}} text-2xl leading-snug mb-3">
              {{services[].title}}
            </h3>
            <p className="text-{{fg}}/60 text-sm leading-relaxed mb-5 font-sans">
              {{services[].body}}
            </p>
            <span className="text-{{fg}}/40 text-xs tracking-widest uppercase font-sans">
              {{services[].price}}
            </span>
          </StaggerItem>
          {/* {{services_list_end}} */}
        </Stagger>

      </div>
    </section>
  );
}
