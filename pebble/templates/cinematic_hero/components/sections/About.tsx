import { Reveal } from "@/components/ui/Reveal";
import Image from "next/image";
import {
  ABOUT_PHOTO_IMAGE,
  ABOUT_HEADLINE,
  ABOUT_BODY,
  TRUST_BADGES,
} from "@/content/site";

export function About() {
  const paragraphs = ABOUT_BODY.split("\n\n").filter(Boolean);

  return (
    <Reveal>
    <section className="py-24">
      <div className="max-w-6xl mx-auto px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-16 items-start">
          {/* Left: photo */}
          <div className="relative aspect-[4/5] w-full rounded-2xl overflow-hidden">
            <Image
              src={ABOUT_PHOTO_IMAGE}
              alt=""
              fill
              sizes="(max-width: 768px) 100vw, 50vw"
              className="object-cover object-center"
            />
          </div>

          {/* Right: copy */}
          <div>
            <h2 className="font-bold text-[36px] text-[var(--color-text-primary)] mb-6">
              {ABOUT_HEADLINE}
            </h2>
            <div className="space-y-4">
              {paragraphs.map((para, i) => (
                <p
                  key={i}
                  className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed"
                >
                  {para}
                </p>
              ))}
            </div>

            {/* Trust badges 2×2 */}
            <div className="mt-10 grid grid-cols-2 gap-6">
              {TRUST_BADGES.map((badge) => (
                <div key={badge.label}>
                  <p className="font-[family-name:var(--font-display)] text-[14px] uppercase tracking-wider text-[var(--color-text-primary)]">
                    {badge.label}
                  </p>
                  <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">
                    {badge.sub}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
    </Reveal>
  );
}
