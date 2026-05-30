import Image from "next/image";

export default function HeroSerene() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-stone-50">
      {/* Full-bleed image — soft natural light, no dark overlay */}
      <div className="absolute inset-0">
        <Image
          src="{{hero_image}}"
          alt="{{headline}}"
          fill
          priority
          className="object-cover"
        />
        {/* Very gentle cream wash so text reads without crushing the image */}
        <div className="absolute inset-0 bg-gradient-to-r from-stone-50/90 via-stone-50/50 to-transparent" />
      </div>

      {/* Content — left-aligned, generous breathing room */}
      <div className="relative z-10 container mx-auto px-8 md:px-16 py-32 max-w-6xl">
        {/* Eyebrow — tiny caps, gold accent */}
        <p className="text-amber-600 text-xs uppercase tracking-[0.25em] mb-6 font-light">
          {{eyebrow}}
        </p>

        {/* Headline — light weight, never aggressive */}
        <h1 className="text-stone-700 text-5xl md:text-7xl font-light leading-[1.1] tracking-tight max-w-2xl">
          {{headline}}
        </h1>

        <p className="text-stone-500 text-xl font-light leading-relaxed mt-8 max-w-xl">
          {{subheadline}}
        </p>

        {/* CTAs — rounded-full, thin border, wide tracking */}
        <div className="mt-12 flex flex-wrap gap-4">
          <a
            href="#book"
            className="inline-block border border-stone-700 text-stone-700 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-amber-600 hover:text-amber-600 transition-colors duration-300"
          >
            {{cta_primary}}
          </a>
          <a
            href="#services"
            className="inline-block border border-stone-300 text-stone-500 px-10 py-4 rounded-full text-xs uppercase tracking-[0.2em] font-light hover:border-stone-500 transition-colors duration-300"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
