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
        <blockquote className="relative" data-pebble-id="pb-ce4983">
          <p className="text-slate-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-278142">
            Our furnace quit on a Tuesday night in February. Northpeak had a tech at our door by 10 PM, diagnosed the problem fast, and had heat running before midnight. Flat-rate price matched exactly what they quoted on the phone. No surprises.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-sky-700/30">
              <Image
                src="https://images.pexels.com/photos/30518659/pexels-photo-30518659.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
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
              <span className="text-slate-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-3d6c86">
                Denver homeowner
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
