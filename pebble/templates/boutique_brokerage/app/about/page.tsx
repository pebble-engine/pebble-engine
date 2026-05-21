import type { Metadata } from "next";
import Image from "next/image";
import { SectionDivider } from "@/components/ui/SectionDivider";
import {
  ABOUT_EYEBROW,
  ABOUT_HEADLINE_LINE_1,
  ABOUT_HEADLINE_LINE_2,
  ABOUT_BODY,
  HERO_IMAGE_URL,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `About | ${SITE_TITLE}`,
};

export default function AboutPage() {
  return (
    <>
      {/* Editorial intro */}
      <section className="bg-bg">
        <div className="page-container pt-32 md:pt-48 pb-section-mobile md:pb-section-desktop">
          <p className="text-label mb-6">{ABOUT_EYEBROW}</p>
          <h1 className="text-display mb-10 max-w-4xl">
            {ABOUT_HEADLINE_LINE_1}
            <br />
            <span className="text-accent">{ABOUT_HEADLINE_LINE_2}</span>
          </h1>
          <div className="grid grid-cols-1 md:grid-cols-12 gap-10 md:gap-16">
            <div className="md:col-span-7 space-y-6">
              {ABOUT_BODY.map((p, i) => (
                <p key={i} className="text-body-lg">
                  {p}
                </p>
              ))}
            </div>
            <div className="md:col-span-5">
              <div className="relative aspect-[4/5] w-full overflow-hidden cinematic-radius bg-surface">
                <Image
                  src={HERO_IMAGE_URL}
                  alt=""
                  fill
                  sizes="(min-width: 1024px) 540px, 100vw"
                  className="object-cover cinematic-img"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="page-container">
        <SectionDivider index="01" label="The bench" />
      </div>
    </>
  );
}
