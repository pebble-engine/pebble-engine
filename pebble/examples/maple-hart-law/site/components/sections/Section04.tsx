"use client";

import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsPanelClean() {
  return (
    <section className="bg-slate-900 py-24 px-8">
      <div className="container mx-auto max-w-6xl">

        {/* Top rule + label */}
        <div className="flex items-center gap-6 mb-16">
          <div className="h-px flex-1 bg-slate-700" aria-hidden="true" />
          <p className="text-sky-500 text-xs font-semibold uppercase tracking-[0.2em] whitespace-nowrap" data-pebble-id="pb-fbba1e">
            Client results
          </p>
          <div className="h-px flex-1 bg-slate-700" aria-hidden="true" />
        </div>

        {/* Quote block */}
        <div className="max-w-3xl mx-auto">
          <FadeUp>
          <blockquote data-pebble-id="pb-b4f4e8">
            <p className="text-slate-100 text-2xl md:text-4xl font-medium leading-snug tracking-tight" data-pebble-id="pb-cb39ea">
              &ldquo;I came in knowing nothing and terrified. Dana sat with me for that first free call and by the end I understood exactly what my custody case would look like and what I needed to do. She never made me feel stupid for asking questions. The outcome was better than I'd hoped.&rdquo;
            </p>

            <footer className="mt-12 flex items-center gap-5">
              {/* Headshot */}
              <div className="relative w-12 h-12 rounded-full overflow-hidden ring-1 ring-sky-500/40 flex-shrink-0">
                <Image
                  src="https://images.pexels.com/photos/36763592/pexels-photo-36763592.jpeg?auto=compress&cs=tinysrgb&h=650&w=940"
                  alt="Rachel Okonkwo"
                  fill
                  priority
                  className="object-cover"
                />
              </div>
              <div>
                <cite className="text-slate-100 text-sm font-semibold not-italic block tracking-wide">
                  Rachel Okonkwo
                </cite>
                <span className="text-slate-400 text-xs tracking-widest uppercase mt-0.5 block" data-pebble-id="pb-2af7e1">
                  Custody client, Burlington
                </span>
              </div>
            </footer>
          </blockquote>
          </FadeUp>
        </div>

      </div>
    </section>
  );
}
