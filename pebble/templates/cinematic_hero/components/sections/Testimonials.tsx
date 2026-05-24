import { TESTIMONIAL_QUOTE, TESTIMONIAL_AUTHOR } from "@/content/site";

export function Testimonials() {
  return (
    <section className="py-24 bg-[var(--color-surface-2)]">
      <div className="max-w-3xl mx-auto px-8 text-center">
        <p
          aria-hidden
          className="font-[family-name:var(--font-display)] text-[96px] leading-none text-[var(--color-accent)] select-none"
        >
          &ldquo;
        </p>
        <blockquote className="mt-2 text-[24px] font-medium italic leading-relaxed text-[var(--color-text-primary)]">
          {TESTIMONIAL_QUOTE}
        </blockquote>
        <p className="mt-6 text-[14px] text-[var(--color-text-secondary)]">
          — {TESTIMONIAL_AUTHOR}
        </p>
      </div>
    </section>
  );
}
