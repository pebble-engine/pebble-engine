import type { Metadata } from "next";
import Image from "next/image";
import { ScriptText } from "@/components/ui/ScriptText";
import { ValuePillars } from "@/components/sections/ValuePillars";
import {
  ABOUT_EYEBROW,
  ABOUT_HEADLINE,
  ABOUT_SCRIPT_ACCENT,
  ABOUT_BODY,
  EDITORIAL_IMAGE_URL,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `About | ${SITE_TITLE}`,
};

export default function AboutPage() {
  return (
    <>
      {/* Editorial intro */}
      <section className="ethereal-bg">
        <div className="page-container pt-20 md:pt-32 pb-section-mobile md:pb-section-desktop">
          <div className="max-w-3xl">
            <p className="text-label mb-4">{ABOUT_EYEBROW}</p>
            <h1 className="text-display mb-2">{ABOUT_HEADLINE}</h1>
            <ScriptText className="text-3xl md:text-4xl block mb-10">
              {ABOUT_SCRIPT_ACCENT}
            </ScriptText>
            <div className="space-y-5">
              {ABOUT_BODY.map((p, i) => (
                <p key={i} className="text-body-lg">
                  {p}
                </p>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Atelier image */}
      <section id="atelier" className="bg-surface">
        <div className="page-container py-section-mobile md:py-section-desktop">
          <div className="relative aspect-[16/8] w-full overflow-hidden rounded-3xl shadow-vapor">
            <Image
              src={EDITORIAL_IMAGE_URL}
              alt="The atelier in SoHo"
              fill
              sizes="(min-width: 1024px) 1280px, 100vw"
              className="object-cover"
            />
          </div>
        </div>
      </section>

      {/* Values — reused from homepage */}
      <ValuePillars />
    </>
  );
}
