import type { Metadata } from "next";
import { About } from "@/components/sections/About";
import { Services } from "@/components/sections/Services";
import { BookingCta } from "@/components/sections/BookingCta";
import {
  ABOUT_PAGE_EYEBROW,
  ABOUT_PAGE_HEADLINE,
  ABOUT_PAGE_INTRO,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `Studio | ${SITE_TITLE}`,
};

export default function AboutPage() {
  return (
    <>
      {/* Editorial intro */}
      <section className="bg-ink-bg pt-32 md:pt-40">
        <div className="page-container pb-section-mobile md:pb-section-desktop">
          <div className="max-w-3xl">
            <p className="text-eyebrow mb-5">{ABOUT_PAGE_EYEBROW}</p>
            <h1 className="text-display mb-8">{ABOUT_PAGE_HEADLINE}</h1>
            <p className="text-body-lg max-w-2xl">{ABOUT_PAGE_INTRO}</p>
          </div>
        </div>
      </section>

      <About />
      <Services />
      <BookingCta />
    </>
  );
}
