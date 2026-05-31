"use client";
import Image from "next/image";
import RevealWords from "@/components/motion/RevealWords";
import Parallax from "@/components/motion/Parallax";
import MagneticButton from "@/components/motion/MagneticButton";

export default function HeroFocused() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-slate-50">
      {/* Background image — right half only, desktop */}
      <div className="absolute inset-y-0 right-0 w-full md:w-1/2">
        <Parallax className="absolute inset-0" distance={40}>
          <Image
            src="{{hero_image}}"
            alt="{{headline}}"
            fill
            priority
            className="object-cover"
          />
        </Parallax>
        <div className="absolute inset-0 bg-gradient-to-r from-slate-50 via-slate-50/60 to-transparent" />
      </div>

      {/* Content — left column */}
      <div className="relative z-10 container mx-auto max-w-6xl px-8 py-28">
        <div className="max-w-xl">
          <p className="text-sky-600 text-xs font-semibold uppercase tracking-[0.2em] mb-6">
            {{eyebrow}}
          </p>
          <h1 className="text-slate-900 text-5xl md:text-7xl font-semibold leading-tight tracking-tight">
            <RevealWords>{{headline}}</RevealWords>
          </h1>
          <p className="text-slate-600 text-lg mt-6 leading-relaxed max-w-md">
            {{subheadline}}
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <MagneticButton
              href="#contact"
              className="inline-block bg-sky-600 text-white px-7 py-3.5 rounded-md font-medium hover:bg-sky-700 transition text-sm tracking-wide"
            >
              {{cta_primary}}
            </MagneticButton>
            <a
              href="#services"
              className="text-slate-700 px-7 py-3.5 rounded-md border border-slate-300 hover:border-slate-400 hover:bg-slate-100 transition text-sm tracking-wide"
            >
              {{cta_secondary}}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
