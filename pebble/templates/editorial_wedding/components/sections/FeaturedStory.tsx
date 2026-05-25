"use client";

import { useRef } from "react";
import Image from "next/image";
import { motion, useScroll, useTransform } from "framer-motion";
import { FEATURED_SLIDES } from "@/content/site";

/**
 * Sticky horizontal-scroll story section.
 * Outer wrapper is 400vh tall; inner is sticky 100vh with a horizontal track
 * driven by useScroll progress.
 */
export function FeaturedStory() {
  const targetRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: targetRef });

  const slideCount = FEATURED_SLIDES.length;
  // Translate from 0% to -((slideCount-1) * 100)%
  const x = useTransform(scrollYProgress, [0, 1], ["0%", `-${(slideCount - 1) * 100}%`]);

  return (
    <section id="featured" ref={targetRef} className="relative" style={{ height: `${slideCount * 100}vh` }}>
      <div className="sticky top-0 h-screen overflow-hidden bg-[#0a0a0a]">
        <motion.div
          style={{ x, width: `${slideCount * 100}%` }}
          className="flex h-full"
        >
          {FEATURED_SLIDES.map((slide, i) => (
            <div key={i} className="h-full flex-shrink-0 flex items-center justify-center px-[10vw] py-16" style={{ width: `${100 / slideCount}%` }}>
              {slide.kind === "intro" && (
                <div className="max-w-3xl mx-auto grid md:grid-cols-2 gap-12 items-center">
                  <div className="relative aspect-[4/5] w-full rounded-sm overflow-hidden">
                    <Image
                      src={slide.image}
                      alt={slide.couple}
                      fill
                      sizes="(max-width: 768px) 100vw, 400px"
                      className="grayscale brightness-75 object-cover"
                    />
                  </div>
                  <div>
                    <p className="text-[#b08d57] text-sm tracking-widest uppercase mb-2">{slide.label}</p>
                    <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-4 text-[#f5f1e8]">
                      {slide.couple}
                    </h2>
                    <p className="text-[#d4a574] font-[family-name:var(--font-display)] italic text-xl mb-6">
                      {slide.venue}
                    </p>
                    <p className="text-[#f5f1e8]/70 leading-relaxed">&ldquo;{slide.quote}&rdquo;</p>
                  </div>
                </div>
              )}
              {slide.kind === "photo" && (
                <div className="relative w-full max-w-5xl h-[75vh] rounded-sm overflow-hidden">
                  <Image
                    src={slide.image}
                    alt={slide.alt}
                    fill
                    sizes="(max-width: 1024px) 100vw, 1024px"
                    className="grayscale brightness-75 object-cover"
                  />
                </div>
              )}
              {slide.kind === "outro" && (
                <div className="text-center">
                  <h3 className="font-[family-name:var(--font-display)] italic text-3xl text-[#f5f1e8] mb-4">
                    {slide.quote}
                  </h3>
                  <p className="text-[#d4a574]">{slide.subline}</p>
                </div>
              )}
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
