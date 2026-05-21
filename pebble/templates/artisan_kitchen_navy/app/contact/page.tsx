import type { Metadata } from "next";
import { Contact } from "@/components/sections/Contact";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import {
  CONTACT_EYEBROW,
  CONTACT_PAGE_HEADLINE,
  CONTACT_PAGE_INTRO,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `Contact | ${SITE_TITLE}`,
};

export default function ContactPage() {
  return (
    <>
      <section className="hero-bg">
        <div className="page-container pt-20 md:pt-28 pb-12 md:pb-16">
          <div className="max-w-2xl">
            <EyebrowChip className="mb-4">{CONTACT_EYEBROW}</EyebrowChip>
            <h1 className="text-display mb-6">{CONTACT_PAGE_HEADLINE}</h1>
            <p className="text-body-lg max-w-xl">{CONTACT_PAGE_INTRO}</p>
          </div>
        </div>
      </section>

      <Contact />
    </>
  );
}
