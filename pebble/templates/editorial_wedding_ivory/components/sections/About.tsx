import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import {
  ABOUT_IMAGE,
  ABOUT_KICKER,
  ABOUT_HEADLINE,
  ABOUT_QUOTE,
  ABOUT_BODY,
} from "@/content/site";

export function About() {
  return (
    <section id="about" className="py-24 px-6 bg-[#1f1a14]/5">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-16 items-center">
        <Reveal>
          <div className="relative w-full aspect-[3/4] rounded-sm overflow-hidden">
            <Image
              src={ABOUT_IMAGE}
              alt="Photographer portrait"
              fill
              sizes="(max-width: 768px) 100vw, 600px"
              className="grayscale object-cover brightness-90"
            />
          </div>
        </Reveal>
        <div className="space-y-6">
          <Reveal>
            <p className="text-[#a47236] text-sm tracking-widest uppercase mb-2">{ABOUT_KICKER}</p>
            <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-4 text-[#1f1a14]">
              {ABOUT_HEADLINE}
            </h2>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-[#1f1a14]/80 leading-relaxed text-lg">&ldquo;{ABOUT_QUOTE}&rdquo;</p>
          </Reveal>
          <Reveal delay={0.2}>
            <p className="text-[#1f1a14]/70 leading-relaxed">{ABOUT_BODY}</p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
