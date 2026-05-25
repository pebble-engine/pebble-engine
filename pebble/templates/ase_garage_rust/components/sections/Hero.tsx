import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import {
  HERO_IMAGE,
  HERO_PILL,
  HERO_HEADLINE,
  HERO_BODY,
  HERO_CTA,
  HERO_CTA_HREF,
  HERO_EMERG_LABEL,
  HERO_EMERG_HREF,
  HERO_TECH_LINE,
} from "@/content/site";

export function Hero() {
  return (
    <section className="bg-[#2a1810] min-h-[90vh] flex items-stretch">
      <div className="grid grid-cols-1 md:grid-cols-2 w-full">
        <div className="p-12 md:p-20 flex flex-col justify-center space-y-8">
          <Reveal>
            <span className="text-[#d97444] uppercase text-xs tracking-[0.2em] font-bold mb-4 block">
              {HERO_PILL}
            </span>
            <h1 className="font-[family-name:var(--font-display)] text-4xl md:text-6xl lg:text-7xl text-[#fafaf9] uppercase leading-[0.9] tracking-tight">
              {HERO_HEADLINE}
            </h1>
          </Reveal>
          <Reveal delay={0.15}>
            <p className="text-[#e7e5e4]/70 text-base md:text-lg max-w-md leading-relaxed">
              {HERO_BODY}
            </p>
          </Reveal>
          <Reveal delay={0.3}>
            <div className="flex flex-col sm:flex-row gap-4">
              <a
                href={HERO_CTA_HREF}
                className="btn-shimmer px-8 py-4 text-center uppercase font-bold rounded-sm tracking-wide"
              >
                {HERO_CTA}
              </a>
              <a
                href={HERO_EMERG_HREF}
                className="btn-brick px-8 py-4 text-center uppercase font-bold rounded-sm tracking-wide"
              >
                {HERO_EMERG_LABEL}
              </a>
            </div>
          </Reveal>
        </div>
        <div className="relative min-h-[300px] md:min-h-0">
          <Image
            src={HERO_IMAGE}
            alt="Mechanic working under hood"
            fill
            priority
            sizes="(max-width: 768px) 100vw, 50vw"
            className="object-cover grayscale hover:grayscale-0 transition-all duration-700"
          />
          <div className="absolute bottom-6 left-6 bg-[#2a1810]/90 px-4 py-2 border-l-2 border-[#d97444]">
            <p className="text-xs text-[#e7e5e4] uppercase tracking-wider">{HERO_TECH_LINE}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
