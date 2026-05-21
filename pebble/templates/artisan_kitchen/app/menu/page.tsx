import type { Metadata } from "next";
import { Menu } from "@/components/sections/Menu";
import { EyebrowChip } from "@/components/ui/EyebrowChip";
import {
  MENU_EYEBROW,
  MENU_PAGE_HEADLINE,
  MENU_PAGE_INTRO,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `Menu | ${SITE_TITLE}`,
};

export default function MenuPage() {
  return (
    <>
      <section className="hero-bg">
        <div className="page-container pt-20 md:pt-28 pb-12 md:pb-16">
          <div className="max-w-2xl">
            <EyebrowChip className="mb-4">{MENU_EYEBROW}</EyebrowChip>
            <h1 className="text-display mb-6">{MENU_PAGE_HEADLINE}</h1>
            <p className="text-body-lg max-w-xl">{MENU_PAGE_INTRO}</p>
          </div>
        </div>
      </section>

      <Menu />
    </>
  );
}
