"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Section header — left-aligned, dominant */}
        <div className="mb-16">
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-4032e8">
            OUR ROSTERS
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black leading-none uppercase max-w-3xl" data-pebble-id="pb-e206ae">
            <RevealWords>TWO GAMES. ONE STANDARD.</RevealWords>
          </h2>
        </div>

        {/* Services grid — dark cards, lime accent on hover */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/9072216/pexels-photo-9072216.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="VALORANT DIVISION"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-cea031">
                VALORANT DIVISION
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-61f334">
                Five players. One shot clock. Our Valorant squad competes in open circuit and collegiate leagues, building rank and rep every week.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-939d14">
                Active
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/9072293/pexels-photo-9072293.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="ROCKET LEAGUE DIVISION"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-e0f6a6">
                ROCKET LEAGUE DIVISION
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-a48232">
                Speed, mechanics, and split-second rotations. The RL roster runs ranked scrims daily and pushes into regional qualifiers each season.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-67b70f">
                Active
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/7047532/pexels-photo-7047532.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="CONTENT & CLIPS"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-eccd2d">
                CONTENT & CLIPS
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-332b97">
                From the signature static glitch intro to highlight reels — our content pipeline turns every match into a moment fans repost.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-7e7eae">
                Live
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/37694861/pexels-photo-37694861.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="SPONSOR PARTNERSHIPS"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-80afed">
                SPONSOR PARTNERSHIPS
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-8ea605">
                Reach a young, engaged audience that lives in Discord, watches Twitch, and wears your brand like a flag. Let's talk numbers.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-ffaee0">
                Open
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
