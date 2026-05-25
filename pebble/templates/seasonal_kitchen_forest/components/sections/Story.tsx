import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { STORY_IMAGE, STORY_HEADLINE, STORY_P1, STORY_P2 } from "@/content/site";

export function Story() {
  return (
    <section className="py-24 px-6 bg-bone">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-24 items-center">
        <Reveal>
          <div className="relative aspect-[4/5] w-full bg-charcoal/10 rounded-sm overflow-hidden">
            <Image
              src={STORY_IMAGE}
              alt="Kitchen prep"
              fill
              sizes="(max-width: 768px) 100vw, 600px"
              className="object-cover grayscale hover:grayscale-0 transition-all duration-700"
            />
          </div>
        </Reveal>
        <div className="space-y-8">
          <Reveal>
            <h2 className="font-[family-name:var(--font-display)] text-4xl md:text-5xl mb-6 text-charcoal">
              {STORY_HEADLINE}
            </h2>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-lg leading-relaxed drop-cap">{STORY_P1}</p>
          </Reveal>
          <Reveal delay={0.2}>
            <p className="text-lg leading-relaxed">{STORY_P2}</p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
