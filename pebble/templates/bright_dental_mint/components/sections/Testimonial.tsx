import { Reveal } from "@/components/ui/Reveal";
import { TESTIMONIAL_QUOTE, TESTIMONIAL_NAME, TESTIMONIAL_META } from "@/content/site";

export function Testimonial() {
  const initial = TESTIMONIAL_NAME.replace(/[^A-Za-z]/g, "").charAt(0) || "A";

  return (
    <section className="py-20 lg:py-28 px-6 bg-slate-50">
      <Reveal>
        <div className="max-w-4xl mx-auto text-center">
          <svg
            className="w-10 h-10 text-mint mx-auto mb-6"
            fill="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path d="M7 7h4v4H8c0 2 1 3 3 3v2c-3 0-5-2-5-5V7zm10 0h4v4h-3c0 2 1 3 3 3v2c-3 0-5-2-5-5V7z" />
          </svg>
          <blockquote className="font-[family-name:var(--font-display)] text-2xl md:text-4xl font-bold text-navy leading-tight mb-8">
            &ldquo;{TESTIMONIAL_QUOTE}&rdquo;
          </blockquote>
          <div className="flex items-center justify-center gap-3">
            <div className="w-10 h-10 bg-ice rounded-full flex items-center justify-center text-navy font-semibold">
              {initial}
            </div>
            <p className="text-slate-600 font-medium">
              {TESTIMONIAL_NAME} · {TESTIMONIAL_META}
            </p>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
