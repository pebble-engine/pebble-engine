import { Reveal } from "@/components/ui/Reveal";
import { MapPin } from "lucide-react";
import {
  SERVICE_AREA_HEADLINE,
  SERVICE_AREA_SUBLINE,
  SERVICE_AREA_MAP_EMBED,
  SERVICE_AREA_CITIES,
} from "@/content/site";

export function ServiceArea() {
  return (
    <section className="py-20 md:py-28 max-w-6xl mx-auto px-6">
      <Reveal>
        <header className="max-w-2xl mb-12">
          <h1 className="font-[family-name:var(--font-display)] text-3xl md:text-5xl uppercase tracking-tight">
            {SERVICE_AREA_HEADLINE}
          </h1>
          <p className="mt-4 text-base md:text-lg text-[var(--color-text-secondary)] leading-relaxed">
            {SERVICE_AREA_SUBLINE}
          </p>
        </header>
      </Reveal>

      <div className="grid grid-cols-1 md:grid-cols-[1.5fr_1fr] gap-8 md:gap-12 items-start">
        <Reveal>
          <div className="aspect-[4/3] md:aspect-auto md:h-full min-h-[400px] rounded-2xl overflow-hidden border border-[var(--color-border)] bg-[var(--color-surface-2)]">
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
              <div className="w-full h-full flex items-center justify-center text-[var(--color-text-secondary)] text-sm">
                [Add your Google Maps embed URL in content/site.ts]
              </div>
            )}
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <ul className="space-y-3">
            {SERVICE_AREA_CITIES.length === 0 ? (
              <li className="text-sm text-[var(--color-text-secondary)]">
                [Add cities you serve in content/site.ts SERVICE_AREA_CITIES array.]
              </li>
            ) : (
              SERVICE_AREA_CITIES.map((city) => (
                <li key={city} className="flex items-center gap-3 text-base">
                  <MapPin className="w-4 h-4 text-[var(--color-accent)] shrink-0" aria-hidden />
                  <span>{city}</span>
                </li>
              ))
            )}
          </ul>
        </Reveal>
      </div>
    </section>
  );
}
