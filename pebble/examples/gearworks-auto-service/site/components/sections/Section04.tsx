"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsQuote() {
  return (
    <section className="bg-slate-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Opening quote mark — oversized decorative glyph */}
        <div
          aria-hidden="true"
          className="text-sky-700/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-04bc17">
          <p className="text-slate-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-c04fa0">
            They sent me photos of my brake rotors before even asking if I wanted the work done. I could actually see the wear for myself. That kind of honesty is rare. I've been bringing both my cars here ever since and I've never once felt like I was being sold something I didn't need.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-sky-700/30">
              <Image
                src="https://images.pexels.com/photos/33435724/pexels-photo-33435724.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Marcus T."
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-slate-900 text-base font-semibold not-italic block">
                Marcus T.
              </cite>
              <span className="text-slate-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-6bdc04">
                Columbus resident, regular customer
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
