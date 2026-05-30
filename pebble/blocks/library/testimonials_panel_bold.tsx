import Image from "next/image";

export default function TestimonialsPanelBold() {
  return (
    <section className="bg-{{bg}} py-24 px-8">
      <div className="container mx-auto max-w-5xl">

        {/* Lime accent bar — top hard rule */}
        <div className="w-16 h-1 bg-{{accent}} mb-12" aria-hidden="true" />

        <blockquote>
          {/* The quote — oversized, dominant */}
          <p className="text-{{fg}} text-3xl md:text-5xl font-black leading-none uppercase tracking-tight max-w-4xl">
            &ldquo;{{quote}}&rdquo;
          </p>

          {/* Attribution row — headshot + name + role inline */}
          <footer className="mt-12 flex items-center gap-5">
            <div className="relative w-14 h-14 overflow-hidden rounded-md ring-2 ring-{{accent}} flex-shrink-0">
              <Image
                src="{{headshot_image}}"
                alt="{{attribution}}"
                fill
                priority
                className="object-cover"
              />
            </div>
            <div>
              <cite className="text-{{fg}} text-sm font-black uppercase tracking-widest not-italic block">
                {{attribution}}
              </cite>
              <span className="text-{{fg}}/50 text-xs uppercase tracking-widest mt-1 block">
                {{role}}
              </span>
            </div>
            {/* Decorative closing rule */}
            <div className="flex-1 h-px bg-{{fg}}/10 ml-4" aria-hidden="true" />
          </footer>
        </blockquote>

      </div>
    </section>
  );
}
