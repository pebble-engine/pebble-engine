"use client";
import Image from "next/image";
import FadeUp from "@/components/motion/FadeUp";

export default function TestimonialsReview() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-4xl">

        {/* Warm decorative rule */}
        <div className="flex items-center gap-4 mb-14 justify-center">
          <span className="h-px w-16 bg-{{accent}}/30" aria-hidden="true" />
          <span className="text-{{accent}}/50 text-xs uppercase tracking-[0.25em] font-sans">
            What people say
          </span>
          <span className="h-px w-16 bg-{{accent}}/30" aria-hidden="true" />
        </div>

        {/* Oversized opening quote glyph */}
        <div
          aria-hidden="true"
          className="text-{{accent}}/15 font-serif text-9xl leading-none select-none text-center -mb-6"
        >
          &ldquo;
        </div>

        {/* Pull-quote */}
        <FadeUp>
        <blockquote className="text-center">
          <p className="text-{{fg}} font-serif text-2xl md:text-4xl leading-snug tracking-tight max-w-3xl mx-auto italic">
            {{quote}}
          </p>

          {/* Attribution */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            <div className="relative w-14 h-14 rounded-full overflow-hidden ring-2 ring-{{accent}}/25">
              <Image
                src="{{headshot_image}}"
                alt="{{attribution}}"
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-{{fg}} font-sans text-sm font-semibold not-italic block">
                {{attribution}}
              </cite>
              <span className="text-{{fg}}/50 font-sans text-xs tracking-wide mt-1 block">
                {{role}}
              </span>
            </div>
          </footer>
        </blockquote>
        </FadeUp>

      </div>
    </section>
  );
}
