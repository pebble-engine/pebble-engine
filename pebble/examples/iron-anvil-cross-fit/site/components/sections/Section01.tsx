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
          <p className="text-lime-400 text-xs font-black uppercase tracking-[0.3em] mb-4" data-pebble-id="pb-8d9951">
            WHAT WE OFFER
          </p>
          <h2 className="text-zinc-50 text-6xl md:text-8xl font-black leading-none uppercase max-w-3xl" data-pebble-id="pb-cce3f6">
            <RevealWords>PROGRAMS BUILT FOR HUMANS</RevealWords>
          </h2>
        </div>

        {/* Services grid — dark cards, lime accent on hover */}
        <Stagger className="grid grid-cols-1 md:grid-cols-3 gap-4">
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/703012/pexels-photo-703012.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="GROUP WODs"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-2a2f2f">
                GROUP WODs
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-435055">
                Daily coached classes scaled to every level. Show up, get after it, leave stronger than you walked in.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-db6f31">
                From $99/mo
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/3775164/pexels-photo-3775164.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="FIRST LIGHT 6AM CREW"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-4b0f42">
                FIRST LIGHT 6AM CREW
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-10d6e7">
                Our legendary sunrise session. Finish the WOD, ring the PR bell, grab coffee from the trailer. The best hour of your day.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-56ccd9">
                Included
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/4853332/pexels-photo-4853332.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="PERSONAL COACHING"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-93f1dc">
                PERSONAL COACHING
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-c4cbdd">
                One-on-one sessions dialing in your technique, programming your goals, and pushing you past what you thought was your limit.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-7d8441">
                From $75/session
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/4853288/pexels-photo-4853288.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="FOUNDATIONS COURSE"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-c74fbf">
                FOUNDATIONS COURSE
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-3d8846">
                Brand new to CrossFit? This is your starting block. Four sessions covering movement basics so your first WOD feels earned, not scary.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-366e8d">
                $120 — 4 sessions
              </span>
            </div>
          </StaggerItem>
          
          <StaggerItem className="group relative bg-zinc-700 overflow-hidden rounded-md hover:ring-2 hover:ring-lime-400 transition-all duration-200">
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src="https://images.pexels.com/photos/34852299/pexels-photo-34852299.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="OPEN GYM"
                fill
                priority
                className="object-cover group-hover:scale-105 transition-transform duration-500 brightness-75"
              />
              {/* Lime accent bar on hover */}
              <div className="absolute bottom-0 left-0 right-0 h-1 bg-lime-400 scale-x-0 group-hover:scale-x-100 transition-transform duration-200 origin-left" />
            </div>
            <div className="p-6">
              <h3 className="text-zinc-50 text-xl font-black uppercase leading-tight mb-2 tracking-tight" data-pebble-id="pb-6b2941">
                OPEN GYM
              </h3>
              <p className="text-zinc-50/60 text-sm leading-snug mb-4" data-pebble-id="pb-bbc225">
                Members get unlimited open floor time. Bring your own programming or chip away at skills on your own schedule.
              </p>
              <span className="text-lime-400 text-sm font-black uppercase tracking-widest" data-pebble-id="pb-71d5cb">
                Members only
              </span>
            </div>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
