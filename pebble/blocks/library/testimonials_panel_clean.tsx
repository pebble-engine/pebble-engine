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
          <p className="text-sky-500 text-xs font-semibold uppercase tracking-[0.2em] whitespace-nowrap">
            Client results
          </p>
          <div className="h-px flex-1 bg-slate-700" aria-hidden="true" />
        </div>

        {/* Quote block */}
        <div className="max-w-3xl mx-auto">
          <FadeUp>
          <blockquote>
            <p className="text-slate-100 text-2xl md:text-4xl font-medium leading-snug tracking-tight">
              &ldquo;{{quote}}&rdquo;
            </p>

            <footer className="mt-12 flex items-center gap-5">
              {/* Headshot */}
              <div className="relative w-12 h-12 rounded-full overflow-hidden ring-1 ring-sky-500/40 flex-shrink-0">
                <Image
                  src="{{headshot_image}}"
                  alt="{{attribution}}"
                  fill
                  priority
                  className="object-cover"
                />
              </div>
              <div>
                <cite className="text-slate-100 text-sm font-semibold not-italic block tracking-wide">
                  {{attribution}}
                </cite>
                <span className="text-slate-400 text-xs tracking-widest uppercase mt-0.5 block">
                  {{role}}
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
