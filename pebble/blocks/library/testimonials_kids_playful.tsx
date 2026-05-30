import Image from "next/image";

export default function TestimonialsKidsPlayful() {
  return (
    <section className="bg-purple-900 py-28 px-8">
      <div className="container mx-auto max-w-4xl text-center">

        {/* Big cheerful quote mark */}
        <div
          aria-hidden="true"
          className="text-pink-400/30 text-9xl font-extrabold leading-none select-none -mb-6"
        >
          &ldquo;
        </div>

        {/* Pull-quote */}
        <blockquote className="relative">
          <p className="text-white text-3xl md:text-5xl font-extrabold leading-tight tracking-tight max-w-3xl mx-auto">
            {{quote}}
          </p>

          {/* Attribution */}
          <footer className="mt-14 flex flex-col items-center gap-5">
            {/* Headshot with colorful ring */}
            <div className="relative w-20 h-20 rounded-full overflow-hidden ring-4 ring-pink-500 shadow-lg shadow-pink-500/40">
              <Image
                src="{{headshot_image}}"
                alt="{{attribution}}"
                fill
                priority
                className="object-cover"
              />
            </div>

            <div>
              <cite className="text-white text-lg font-extrabold not-italic block">
                {{attribution}}
              </cite>
              <span className="text-pink-300 text-sm tracking-wide mt-1 block">
                {{role}}
              </span>
            </div>

            {/* Star rating — decorative */}
            <div aria-hidden="true" className="flex gap-1 text-amber-300 text-2xl mt-1">
              &#9733;&#9733;&#9733;&#9733;&#9733;
            </div>
          </footer>
        </blockquote>

      </div>
    </section>
  );
}
