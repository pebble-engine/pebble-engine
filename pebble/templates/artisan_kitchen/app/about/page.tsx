import type { Metadata } from "next";
import Image from "next/image";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import { Features } from "@/components/sections/Features";
import {
  ABOUT_EYEBROW,
  ABOUT_PAGE_HEADLINE,
  ABOUT_PAGE_BODY,
  ABOUT_IMAGE_URL,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `About | ${SITE_TITLE}`,
};

export default function AboutPage() {
  return (
    <>
      {/* Editorial intro */}
      <section className="hero-bg">
        <div className="page-container pt-20 md:pt-28 pb-section-mobile md:pb-section-desktop">
          <div className="max-w-3xl">
            <EyebrowChip className="mb-4">{ABOUT_EYEBROW}</EyebrowChip>
            <h1 className="text-display mb-8">{ABOUT_PAGE_HEADLINE}</h1>
            <div className="space-y-5">
              {ABOUT_PAGE_BODY.map((p, i) => (
                <p key={i} className="text-body-lg">
                  {p}
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Atelier image — wide */}
      <section className="bg-cream">
        <div className="page-container py-section-mobile md:py-section-desktop">
          <div className="relative aspect-[16/8] w-full overflow-hidden rounded-4xl warm-shadow-strong">
            <Image
              src={ABOUT_IMAGE_URL}
              alt="Inside the bakery"
              fill
              sizes="(min-width: 1024px) 1280px, 100vw"
              className="object-cover"
            />
          </div>
        </div>
      </section>

      {/* Reuse the three-card feature grid */}
      <Features />
    </>
  );
}
