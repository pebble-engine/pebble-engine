import Image from "next/image";

export default function HeroFullbleedEditorial() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden bg-neutral-900">
      {/* Full-bleed image — no overlay, the photograph speaks */}
      <div className="absolute inset-0">
        <Image
          src="{{hero_image}}"
          alt="{{headline}}"
          fill
          priority
          className="object-cover"
        />
      </div>

      {/* Floating type — bottom-left, deliberately small against the frame */}
      <div className="relative z-10 px-8 md:px-16 pb-14 md:pb-20 max-w-2xl">
        <p className="text-neutral-300 text-xs uppercase tracking-widest mb-5 font-sans">
          {{eyebrow}}
        </p>
        <h1 className="font-serif text-neutral-50 text-4xl md:text-6xl leading-tight mb-6">
          {{headline}}
        </h1>
        <p className="text-neutral-300 text-base leading-relaxed mb-8 max-w-sm font-sans">
          {{subheadline}}
        </p>
        <div className="flex flex-wrap gap-6 items-center">
          <a
            href="#work"
            className="text-neutral-50 text-sm tracking-wide border-b border-neutral-50/60 pb-px hover:border-neutral-50 transition-colors"
          >
            {{cta_primary}}
          </a>
          <a
            href="#about"
            className="text-neutral-400 text-sm tracking-wide hover:text-neutral-200 transition-colors"
          >
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
