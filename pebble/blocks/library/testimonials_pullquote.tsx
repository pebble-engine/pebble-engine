import Image from "next/image";

export default function TestimonialsQuote() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Opening quote mark — oversized decorative glyph */}
        <div
          aria-hidden="true"
          className="text-{{accent}}/20 text-9xl font-serif leading-none select-none -mb-8"
        >
          &ldquo;
        </div>

        {/* The pull-quote itself */}
        <blockquote className="relative">
          <p className="text-{{fg}} text-3xl md:text-5xl font-semibold leading-tight tracking-tight max-w-3xl mx-auto">
            {{quote}}
          </p>

          {/* Attribution block */}
          <footer className="mt-12 flex flex-col items-center gap-4">
            {/* Headshot circle */}
            <div className="relative w-16 h-16 rounded-full overflow-hidden ring-2 ring-{{accent}}/30">
              <Image
                src="{{headshot_image}}"
                alt="{{attribution}}"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-{{fg}} text-base font-semibold not-italic block">
                {{attribution}}
              </cite>
              <span className="text-{{fg}}/50 text-sm tracking-wide mt-1 block">
                {{role}}
              </span>
            </div>
          </footer>
        </blockquote>

      </div>
    </section>
  );
}
