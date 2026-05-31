"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger } from "@/components/motion/Stagger";
import TiltCard from "@/components/motion/TiltCard";

export default function ServicesCardsPlayful() {
  return (
    <section className="bg-purple-100 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header */}
        <div className="text-center mb-16">
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide">
            {{eyebrow}}
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto">
            <RevealWords>{{headline}}</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* {{services_list_start}} */}
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="{{services[].image}}"
                alt="{{services[].title}}"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                {{services[].price}}
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug">
                {{services[].title}}
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed">
                {{services[].body}}
              </p>
            </div>
          </TiltCard>
          {/* {{services_list_end}} */}
        </Stagger>
      </div>
    </section>
  );
}
