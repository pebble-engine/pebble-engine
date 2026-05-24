import { Reveal } from "@/components/ui/Reveal";
import {
  SERVICE_AREA_HEADLINE,
  SERVICE_AREA_SUBLINE,
  SERVICE_AREA_MAP_EMBED,
  SERVICE_AREA_CITIES,
} from "@/content/site";

export function ServiceArea() {
  return (
    <section className="relative py-20 sm:py-28">
      <div className="mx-auto max-w-6xl px-6">
        <Reveal>
          <div className="max-w-2xl mb-12">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
              Service area
            </p>
            <h1 className="mt-3 font-display text-4xl font-bold tracking-tight text-fg sm:text-5xl">
              {SERVICE_AREA_HEADLINE}
            </h1>
            <p className="mt-4 text-base text-muted leading-relaxed">
              {SERVICE_AREA_SUBLINE}
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-[1.5fr_1fr] gap-8 md:gap-12 items-start">
          <Reveal>
            <div className="aspect-[4/3] md:aspect-auto md:h-full min-h-[400px] rounded-2xl overflow-hidden border border-border bg-card/60">
              {SERVICE_AREA_MAP_EMBED ? (
                <iframe
                  src={SERVICE_AREA_MAP_EMBED}
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="Service area map"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted text-sm px-6 text-center">
                  [Add your Google Maps embed URL in content/site.ts]
                </div>
              )}
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <ul className="space-y-3">
              {SERVICE_AREA_CITIES.length === 0 ? (
                <li className="text-sm text-muted">
                  [Add cities you serve in content/site.ts SERVICE_AREA_CITIES array.]
                </li>
              ) : (
                SERVICE_AREA_CITIES.map((city) => (
                  <li key={city} className="flex items-center gap-3 text-base text-fg/90">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-primary shrink-0" aria-hidden="true">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                      <circle cx="12" cy="10" r="3" />
                    </svg>
                    <span>{city}</span>
                  </li>
                ))
              )}
            </ul>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
