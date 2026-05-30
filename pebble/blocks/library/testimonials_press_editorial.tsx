export default function TestimonialsPressEditorial() {
  return (
    <section className="bg-{{bg}} py-28 px-8">
      <div className="container mx-auto max-w-3xl">

        {/* Rule above — editorial breath */}
        <div className="border-t border-{{fg}}/15 pt-16">

          {/* Oversized opening mark — hairline weight only */}
          <div
            aria-hidden="true"
            className="font-serif text-{{fg}}/10 text-8xl leading-none select-none -mb-4"
          >
            &ldquo;
          </div>

          <blockquote>
            <p className="font-serif text-{{fg}} text-2xl md:text-4xl leading-snug tracking-tight">
              {{quote}}
            </p>

            <footer className="mt-12 flex items-center gap-6">
              {/* Minimal horizontal rule in lieu of headshot */}
              <div className="w-8 h-px bg-{{fg}}/25 flex-shrink-0" aria-hidden="true" />
              <div>
                <cite className="text-{{fg}} text-sm font-sans tracking-wide not-italic block">
                  {{attribution}}
                </cite>
                <span className="text-{{fg}}/40 text-xs font-sans tracking-widest uppercase mt-1 block">
                  {{role}}
                </span>
              </div>
            </footer>
          </blockquote>

        </div>
      </div>
    </section>
  );
}
