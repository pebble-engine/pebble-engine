"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesMenu() {
  return (
    <section className="bg-stone-50 py-32 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Section header — centered, airy */}
        <div className="text-center mb-20">
          <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-5 font-light">
            {{eyebrow}}
          </p>
          <h2 className="text-stone-700 text-5xl md:text-6xl font-light leading-tight max-w-xl mx-auto tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services — stacked menu rows with image thumbnails */}
        <Stagger className="divide-y divide-stone-200">
          {/* {{services_list_start}} */}
          <StaggerItem className="group flex items-center gap-8 py-10 hover:bg-stone-100/60 transition-colors duration-300 px-4 -mx-4 rounded-2xl">
            {/* Thumbnail */}
            <div className="relative flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
            </div>

            {/* Copy */}
            <div className="flex-1 min-w-0">
              <h3 className="text-stone-700 text-xl font-light leading-snug mb-1 tracking-tight">
                {{services[].title}}
              </h3>
              <p className="text-stone-400 text-base font-light leading-relaxed truncate">
                {{services[].body}}
              </p>
            </div>

            {/* Price */}
            <div className="flex-shrink-0 text-right">
              <span className="text-amber-600 text-base font-light tracking-wide">
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
