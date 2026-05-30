import Image from "next/image";

export default function TestimonialsWhisper() {
  return (
    <section className="bg-stone-100 py-32 px-8">
      <div className="container mx-auto max-w-3xl text-center">

        {/* Thin horizontal rule — the only decoration */}
        <div className="w-12 h-px bg-amber-600/40 mx-auto mb-16" aria-hidden="true" />

        {/* The quote — light weight, generous tracking */}
        <blockquote>
          <p className="text-stone-700 text-2xl md:text-4xl font-light leading-relaxed tracking-tight max-w-2xl mx-auto italic">
            &ldquo;{{quote}}&rdquo;
          </p>

          {/* Attribution — small, calm */}
          <footer className="mt-14 flex flex-col items-center gap-4">
            {/* Headshot — very small, soft ring */}
            <div className="relative w-12 h-12 rounded-full overflow-hidden ring-1 ring-amber-600/20">
              <Image
                src="{{headshot_image}}"
                alt="{{attribution}}"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-stone-600 text-sm font-light not-italic block tracking-wide uppercase">
                {{attribution}}
              </cite>
              <span className="text-stone-400 text-xs font-light tracking-widest mt-1 block uppercase">
                {{role}}
              </span>
            </div>
          </footer>
        </blockquote>

        {/* Closing rule */}
        <div className="w-12 h-px bg-amber-600/40 mx-auto mt-16" aria-hidden="true" />

      </div>
    </section>
  );
}
