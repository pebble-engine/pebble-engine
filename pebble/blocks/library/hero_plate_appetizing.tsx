import Image from "next/image";

export default function HeroPlate() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden bg-stone-900">
      {/* Full-bleed food photograph */}
      <div className="absolute inset-0">
        <Image
          src="{{hero_image}}"
          alt="{{headline}}"
          fill
          priority
          className="object-cover"
        />
        {/* Rich warm gradient — bottom-heavy so type is readable */}
        <div className="absolute inset-0 bg-gradient-to-t from-stone-900 via-stone-900/60 to-transparent" />
      </div>

      {/* Copy block — sits beneath the photo like a menu caption */}
      <div className="relative z-10 container mx-auto px-8 pb-20 md:pb-28 max-w-6xl">
        <p className="text-{{accent}} text-sm uppercase tracking-widest font-sans mb-4">
          {{eyebrow}}
        </p>
        <h1 className="text-stone-50 font-serif text-5xl md:text-7xl leading-tight max-w-3xl mb-6">
          {{headline}}
        </h1>
        <p className="text-stone-200/80 text-lg md:text-xl font-sans leading-relaxed max-w-2xl mb-10">
          {{subheadline}}
        </p>
        <div className="flex flex-wrap gap-4">
          <a
            href="#reserve"
            className="bg-{{accent}} text-{{accent_fg}} px-8 py-4 rounded-full font-sans font-semibold hover:scale-105 hover:opacity-95 transition-transform duration-200"
          >
            {{cta_primary}}
          </a>
          <a
            href="#menu"
            className="text-stone-100 px-8 py-4 rounded-full border border-stone-400/40 font-sans hover:bg-stone-50/10 transition"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
