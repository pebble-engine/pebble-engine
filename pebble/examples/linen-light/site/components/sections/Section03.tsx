"use client";

import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import { Stagger, StaggerItem } from "@/components/motion/Stagger";

export default function ServicesGridEditorial() {
  return (
    <section className="bg-neutral-50 py-28 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Sparse header — left-aligned, no centering */}
        <div className="mb-16 border-b border-neutral-900/10 pb-10">
          <p className="text-neutral-200 text-xs uppercase tracking-widest mb-4 font-sans" data-pebble-id="pb-186a37">
            Work
          </p>
          <h2 className="font-serif text-neutral-900 text-4xl md:text-5xl leading-tight max-w-xl" data-pebble-id="pb-f1f6b8">
            <RevealWords>Honest coverage for the day as it unfolds.</RevealWords>
          </h2>
        </div>

        {/* Services — two-column editorial grid */}
        <Stagger className="grid grid-cols-1 md:grid-cols-2 gap-px bg-neutral-900/8">
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/6609721/pexels-photo-6609721.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Full-Day Wedding Coverage"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-5f48cb">
              Full-Day Wedding Coverage
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-e1e6bd">
              Eight to ten hours on 35mm and 120 film. Getting ready through the last dance. Every roll developed and scanned by hand.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-d18fc7">
              From $3,800
            </span>
          </StaggerItem>
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/18627876/pexels-photo-18627876.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Ceremony & Portraits"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-f96d93">
              Ceremony & Portraits
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-837be9">
              A focused half-day: the ceremony, the quiet hour after, and portraits in whatever light we find. Four to five hours.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-4f34aa">
              From $2,200
            </span>
          </StaggerItem>
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/15878600/pexels-photo-15878600.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Elopements"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-c3c5e8">
              Elopements
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-4a89d9">
              Just the two of you and a few rolls of film. A morning on a ridge, a backyard, a courthouse. Unhurried and personal.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-7315d9">
              From $1,400
            </span>
          </StaggerItem>
          
          <StaggerItem className="bg-neutral-50 p-10 group">
            <div className="relative aspect-[4/3] overflow-hidden mb-8">
              <Image
                src="https://images.pexels.com/photos/7206205/pexels-photo-7206205.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Hand-Developed Black & White"
                fill
                priority
                className="object-cover grayscale group-hover:grayscale-0 transition-all duration-700"
              />
            </div>
            <h3 className="font-serif text-neutral-900 text-2xl leading-snug mb-3" data-pebble-id="pb-cc618d">
              Hand-Developed Black & White
            </h3>
            <p className="text-neutral-900/60 text-sm leading-relaxed mb-5 font-sans" data-pebble-id="pb-d61500">
              All black-and-white film is developed in my darkroom. The grain and tones you see are mine — no filter, no simulation.
            </p>
            <span className="text-neutral-900/40 text-xs tracking-widest uppercase font-sans" data-pebble-id="pb-f23622">
              Included
            </span>
          </StaggerItem>
          
        </Stagger>

      </div>
    </section>
  );
}
