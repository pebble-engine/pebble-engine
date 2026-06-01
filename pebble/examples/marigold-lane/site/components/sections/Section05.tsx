"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsWhisper() {
  return (
    <section className="bg-stone-100 py-32 px-8">
      <div className="container mx-auto max-w-3xl text-center">

        {/* Thin horizontal rule — the only decoration */}
        <div className="w-12 h-px bg-amber-600/40 mx-auto mb-16" aria-hidden="true" />

        {/* The quote — light weight, generous tracking */}
        <FadeUp>
        <blockquote data-pebble-id="pb-c2daa8">
          <p className="text-stone-700 text-2xl md:text-4xl font-light leading-relaxed tracking-tight max-w-2xl mx-auto italic" data-pebble-id="pb-2e4220">
            &ldquo;I've moved twice and still drive across the city to get to Marigold Lane. They know my hair better than I do — and the tea and sit-down at the start of every visit is something I genuinely look forward to.&rdquo;
          </p>

          {/* Attribution — small, calm */}
          <footer className="mt-14 flex flex-col items-center gap-4">
            {/* Headshot — very small, soft ring */}
            <div className="relative w-12 h-12 rounded-full overflow-hidden ring-1 ring-amber-600/20">
              <Image
                src="https://images.pexels.com/photos/19757239/pexels-photo-19757239.png?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="Rosalind"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-stone-600 text-sm font-light not-italic block tracking-wide uppercase">
                Rosalind
              </cite>
              <span className="text-stone-400 text-xs font-light tracking-widest mt-1 block uppercase" data-pebble-id="pb-d6cc0c">
                Client since the beginning.
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

        {/* Closing rule */}
        <div className="w-12 h-px bg-amber-600/40 mx-auto mt-16" aria-hidden="true" />

      </div>
    </section>
  );
}
