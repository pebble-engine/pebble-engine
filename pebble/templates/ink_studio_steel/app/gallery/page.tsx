import type { Metadata } from "next";
import { GalleryCard } from "@/components/ui/GalleryCard";
import { BookingCta } from "@/components/sections/BookingCta";
import {
  GALLERY_PAGE_EYEBROW,
  GALLERY_PAGE_HEADLINE,
  GALLERY_PAGE_INTRO,
  GALLERY_ITEMS,
  SITE_TITLE,
} from "@/content/site";

export const metadata: Metadata = {
  title: `Gallery | ${SITE_TITLE}`,
};

export default function GalleryPage() {
  return (
    <>
      <section className="bg-ink-bg pt-32 md:pt-40">
        <div className="page-container pb-12 md:pb-16">
          <div className="max-w-3xl">
            <p className="text-eyebrow mb-5">{GALLERY_PAGE_EYEBROW}</p>
            <h1 className="text-display mb-6">{GALLERY_PAGE_HEADLINE}</h1>
            <p className="text-body-lg max-w-2xl">{GALLERY_PAGE_INTRO}</p>
          </div>
        </div>
      </section>

      {GALLERY_ITEMS.length > 0 && (
        <section
          aria-labelledby="gallery-grid-heading"
          className="bg-ink-bg"
        >
          <div className="page-container pb-section-mobile md:pb-section-desktop">
            <h2 id="gallery-grid-heading" className="sr-only">
              Portfolio
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
              {GALLERY_ITEMS.map((item) => (
                <GalleryCard
                  key={item.id}
                  title={item.title}
                  style={item.style}
                  imageUrl={item.image_url}
                  alt={item.alt}
                />
              ))}
            </div>
          </div>
        </section>
      )}

      <BookingCta />
    </>
  );
}
