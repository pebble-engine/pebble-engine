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
          <blockquote data-pebble-id="pb-995c8f">
          {/* The quote — oversized, dominant */}
          <p className="text-zinc-50 text-3xl md:text-5xl font-black leading-none uppercase tracking-tight max-w-4xl" data-pebble-id="pb-bbf9cf">
            &ldquo;I showed up not knowing a clean from a deadlift. Twelve weeks later I hit a 185lb back squat and rang that bell so hard. This crew makes you believe you can do things you never thought possible.&rdquo;
          </p>

          {/* Attribution row — headshot + name + role inline */}
          <footer className="mt-12 flex items-center gap-5">
            <div className="relative w-14 h-14 overflow-hidden rounded-md ring-2 ring-lime-400 flex-shrink-0">
              <Image
                src="https://images.pexels.com/photos/7777272/pexels-photo-7777272.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                alt="SARAH KOWALSKI"
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-zinc-50 text-sm font-black uppercase tracking-widest not-italic block">
                SARAH KOWALSKI
              </cite>
              <span className="text-zinc-50/50 text-xs uppercase tracking-widest mt-1 block" data-pebble-id="pb-163df4">
                MEMBER SINCE 2022 — FIRST LIGHT CREW
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
