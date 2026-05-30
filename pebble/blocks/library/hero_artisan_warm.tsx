import Image from "next/image";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-end overflow-hidden">
      <div className="absolute inset-0">
        <Image
          src="{{hero_image}}"
          alt="{{headline}}"
          fill
          priority
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-{{bg}} via-{{bg}}/40 to-transparent" />
      </div>
      <div className="relative z-10 container mx-auto px-8 pb-24">
        <p className="text-{{accent}} text-sm uppercase tracking-widest mb-4">
          {{eyebrow}}
        </p>
        <h1 className="text-{{fg}} text-6xl md:text-8xl font-bold leading-none max-w-4xl">
          {{headline}}
        </h1>
        <p className="text-{{fg}}/80 text-xl mt-6 max-w-2xl leading-relaxed">
          {{subheadline}}
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <a href="#order"
             className="bg-{{accent}} text-{{bg}} px-8 py-4 rounded-full font-semibold hover:opacity-90 transition">
            {{cta_primary}}
          </a>
          <a href="#about"
             className="text-{{fg}} px-8 py-4 rounded-full border border-{{fg}}/30 hover:bg-{{fg}}/10 transition">
            {{cta_secondary}}
          </a>
        </div>
      </div>
    </section>
  );
}
