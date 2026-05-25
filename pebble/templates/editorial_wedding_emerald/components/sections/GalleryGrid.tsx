import Image from "next/image";
import { Reveal } from "@/components/ui/Reveal";
import { GALLERY } from "@/content/site";

export function GalleryGrid() {
  return (
    <section className="py-24 px-6 bg-[#0a2820]">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <h2 className="font-[family-name:var(--font-display)] italic text-4xl md:text-5xl mb-12 text-center text-[#f5f0dc]">
            Selected Weddings
          </h2>
        </Reveal>
        <div className="masonry-ed">
          {GALLERY.map((g, i) => (
            <div key={i} className="masonry-item-ed group cursor-pointer">
              <Image
                src={g.image}
                alt={g.couple}
                width={600}
                height={800}
                sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                className="w-full h-auto grayscale brightness-75 block group-hover:grayscale-0 group-hover:brightness-100 transition-all duration-700"
              />
              <div className="absolute inset-0 flex flex-col justify-end p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-t from-[#0a2820]/90 to-transparent">
                <p className="font-[family-name:var(--font-display)] italic text-xl text-[#c9a96e]">
                  {g.couple}
                </p>
                <p className="text-xs text-[#f5f0dc]/70 uppercase tracking-wider">{g.meta}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
