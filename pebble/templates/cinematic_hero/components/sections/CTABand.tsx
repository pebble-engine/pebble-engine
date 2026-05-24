import {
  CTA_BAND_HEADLINE,
  CTA_BAND_BODY,
  CTA_BAND_LABEL,
  CTA_BAND_HREF,
} from "@/content/site";

export function CTABand() {
  return (
    <section className="bg-[var(--color-accent)] text-white">
      <div className="max-w-5xl mx-auto px-8 py-16 md:py-24 flex flex-col md:flex-row md:items-end md:justify-between gap-6">
        <div className="max-w-xl">
          <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl uppercase tracking-tight">
            {CTA_BAND_HEADLINE}
          </h2>
          <p className="mt-3 text-base md:text-lg text-white/90 leading-relaxed">
            {CTA_BAND_BODY}
          </p>
        </div>
        <a
          href={CTA_BAND_HREF}
          className="inline-flex items-center justify-center h-14 px-7 rounded-full bg-white text-[var(--color-accent-dark)] font-bold text-base hover:bg-white/95 transition-colors shrink-0"
        >
          {CTA_BAND_LABEL}
        </a>
      </div>
    </section>
  );
}
