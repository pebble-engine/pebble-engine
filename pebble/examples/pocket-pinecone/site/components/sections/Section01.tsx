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
          <p className="inline-flex items-center gap-2 bg-pink-500 text-white text-sm font-bold px-5 py-2 rounded-full mb-5 tracking-wide" data-pebble-id="pb-8e2261">
            🧩 What's in store
          </p>
          <h2 className="text-purple-900 text-5xl md:text-6xl font-extrabold leading-tight max-w-2xl mx-auto" data-pebble-id="pb-8648cf">
            <RevealWords>Toys that spark imagination, not just screen time</RevealWords>
          </h2>
        </div>

        {/* Services grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-8">
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/3663061/pexels-photo-3663061.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Wooden Toys & Figures"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                From $12
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-9132d0">
                Wooden Toys & Figures
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-457d64">
                Beautifully crafted animals, cars, dollhouses, and more — all solid wood, all built to last a childhood and then some.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/7269701/pexels-photo-7269701.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Open-Ended Building Sets"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                From $24
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-1de3cc">
                Open-Ended Building Sets
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-e73665">
                Blocks, tiles, and loose parts that can become anything a kid dreams up. No right answer, no batteries required.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/12585769/pexels-photo-12585769.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Weird Wind-Up Critters"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                From $6
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-42540e">
                Weird Wind-Up Critters
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-fb94f1">
                Our most beloved oddities — waddling penguins, flipping frogs, chomping crabs. Kids lose their minds for them every single time.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/10388909/pexels-photo-10388909.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Games You Won't Find Elsewhere"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                From $18
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-d0d14e">
                Games You Won't Find Elsewhere
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-2e2003">
                Strategy, silliness, and storytelling — we scout indie games and import gems that never make it to the big-box stores.
              </p>
            </div>
          </TiltCard>
          
          <TiltCard className="group bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300 ring-2 ring-pink-100">
            {/* Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/1303087/pexels-photo-1303087.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="The Mystery Cubby Wall 🎉"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500"
              />
              {/* Colorful top-corner badge */}
              <div className="absolute top-3 right-3 bg-amber-300 text-purple-900 text-xs font-extrabold px-3 py-1 rounded-full shadow">
                $5 each
              </div>
            </div>
            {/* Card body */}
            <div className="p-7">
              <h3 className="text-purple-900 text-xl font-extrabold mb-2 leading-snug" data-pebble-id="pb-bd5185">
                The Mystery Cubby Wall 🎉
              </h3>
              <p className="text-purple-900/65 text-base leading-relaxed" data-pebble-id="pb-a04ec4">
                Our numbered wooden boxes up front, each hiding a small surprise toy for just $5. Kids beg to pick one every single visit — and honestly, so do the parents.
              </p>
            </div>
          </TiltCard>
          
        </Stagger>
      </div>
    </section>
  );
}
