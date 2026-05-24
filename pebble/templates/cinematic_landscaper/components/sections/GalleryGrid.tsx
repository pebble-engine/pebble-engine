import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { GALLERY_HEADLINE, GALLERY_SUBLINE, GALLERY_IMAGES } from "@/content/site";

export function GalleryGrid() {
  return (
    <section className="py-20 md:py-28 max-w-6xl mx-auto px-6">
      <Reveal>
        <header className="max-w-2xl mb-12">
          <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-5xl uppercase tracking-tight">
            {GALLERY_HEADLINE}
          </h1>
          <p className="mt-4 text-base md:text-lg text-[var(--color-text-secondary)] leading-relaxed">
            {GALLERY_SUBLINE}
          </p>
        </header>
      </Reveal>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {GALLERY_IMAGES.map((img, i) => (
          <Reveal key={img.src} delay={i * 0.08} className="group">
            <div className="aspect-[4/3] relative overflow-hidden rounded-2xl bg-[var(--color-surface-2)]">
              <Image
                src={img.src}
                alt={img.alt}
                fill
                sizes="(min-width:1024px) 33vw, (min-width:640px) 50vw, 100vw"
                className="object-cover transition-transform duration-500 group-hover:scale-105"
              />
            </div>
            {img.caption && (
              <p className="mt-2 text-sm text-[var(--color-text-secondary)]">{img.caption}</p>
            )}
          </Reveal>
        ))}
      </div>
    </section>
  );
}
