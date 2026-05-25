import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { GALLERY_IMAGES } from "@/content/site";

export function Gallery() {
  return (
    <section className="py-24 px-6 bg-bone">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] text-4xl md:text-5xl mb-12 text-center text-charcoal">
            In the Room
          </h2>
        </Reveal>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {GALLERY_IMAGES.map((g, i) => (
            <Reveal key={i} delay={i * 0.05}>
              <div className="group overflow-hidden rounded-sm aspect-[4/5] relative">
                <Image
                  src={g.src}
                  alt={g.alt}
                  fill
                  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                  className="object-cover transition-transform duration-700 group-hover:scale-105"
                />
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
