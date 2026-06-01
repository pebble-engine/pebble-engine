"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsPanelBold() {
  return (
    <section className="bg-zinc-900 py-24 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Lime accent bar — top hard rule */}
        <div className="w-16 h-1 bg-lime-400 mb-12" aria-hidden="true" />

        <FadeUp>
          <blockquote data-pebble-id="pb-a1017d">
          {/* The quote — oversized, dominant */}
          <p className="text-zinc-50 text-3xl md:text-5xl font-black leading-none uppercase tracking-tight max-w-4xl" data-pebble-id="pb-3cf4d1">
            &ldquo;The static glitch drops and the whole lobby knows. Doesn't matter what server — when that intro hits, SV is in the building. I've watched that clip fifty times.&rdquo;
          </p>

          {/* Attribution row — headshot + name + role inline */}
          <footer className="mt-12 flex items-center gap-5">
            <div className="relative w-14 h-14 overflow-hidden rounded-md ring-2 ring-lime-400 flex-shrink-0">
              <Image
                src="https://images.pexels.com/photos/7915379/pexels-photo-7915379.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="KAI MERRITT"
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-zinc-50 text-sm font-black uppercase tracking-widest not-italic block">
                KAI MERRITT
              </cite>
              <span className="text-zinc-50/50 text-xs uppercase tracking-widest mt-1 block" data-pebble-id="pb-09b250">
                CONTENT CREATOR, 280K TWITCH FOLLOWERS
              </span>
            </div>
            {/* Decorative closing rule */}
            <div className="flex-1 h-px bg-zinc-50/10 ml-4" aria-hidden="true" />
          </footer>
          </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
