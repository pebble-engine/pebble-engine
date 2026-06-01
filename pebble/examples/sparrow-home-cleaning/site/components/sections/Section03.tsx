"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsQuote() {
  return (
    <section className="bg-sky-50 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Opening quote mark — oversized decorative glyph */}
        <div
          aria-hidden="true"
          className="text-sky-600/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <FadeUp>
        <blockquote className="relative" data-pebble-id="pb-110985">
          <p className="text-slate-900 text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto" data-pebble-id="pb-72a8d0">
            I was skeptical I'd ever find a cleaning service I could actually rely on — but Sparrow sends the same two people every biweekly visit and my house has never looked better. They noticed a stain I'd given up on and got it out without me even asking. That kind of detail matters.
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-sky-600/30">
              <Image
                src="https://images.pexels.com/photos/29326589/pexels-photo-29326589.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Rachel M."
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-slate-900 text-base font-semibold not-italic block">
                Rachel M.
              </cite>
              <span className="text-slate-900/50 text-sm tracking-wide mt-1 block" data-pebble-id="pb-c81111">
                Recurring biweekly customer, South Minneapolis
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
