import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { CTABand } from "@/components/sections/CTABand";
import { ABOUT_HEADLINE, ABOUT_BODY, TRUST_BADGES } from "@/content/site";
import Image from "next/image";
import { ABOUT_PHOTO_IMAGE } from "@/content/site";

export default function AboutPage() {
  const paragraphs = ABOUT_BODY.split("\n\n").filter(Boolean);

  return (
    <>
      <Navbar />
      <main className="flex-1">
        <section className="py-24">
          <div className="max-w-4xl mx-auto px-8">
            <h1 className="font-bold text-[36px] md:text-[44px] text-[var(--color-text-primary)] mb-8">
              {ABOUT_HEADLINE}
            </h1>

            <div className="relative aspect-[16/7] w-full rounded-2xl overflow-hidden mb-10">
              <Image
                src={ABOUT_PHOTO_IMAGE}
                alt=""
                fill
                sizes="(max-width: 1024px) 100vw, 896px"
                className="object-cover object-center"
              />
            </div>

            <div className="space-y-5 mb-16">
              {paragraphs.map((para, i) => (
                <p
                  key={i}
                  className="text-[17px] text-[var(--color-text-secondary)] leading-relaxed"
                >
                  {para}
                </p>
              ))}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {TRUST_BADGES.map((badge) => (
                <div key={badge.label}>
                  <p className="font-[family-name:var(--font-display)] text-[14px] uppercase tracking-wider text-[var(--color-text-primary)]">
                    {badge.label}
                  </p>
                  <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
                    {badge.sub}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <CTABand />
      </main>
      <Footer />
    </>
  );
}
