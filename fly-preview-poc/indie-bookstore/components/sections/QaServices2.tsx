"use client";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

export function QaServices2() {
  return (
    <section className="max-w-prose mx-auto px-6 md:px-12 py-24 md:py-32">
      <FadeIn delay={0.2} duration={0.9}>
        <h2
          className="font-display italic text-[4rem] leading-none text-[var(--color-text-muted)] mb-8"
          style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-435210">
          II.
        </h2>
      </FadeIn>

      <ScrollReveal direction="up" delay={0.1} duration={0.9}>
        <div
          className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)] mb-6"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-24abc6">
            &quot;I miss the feeling of flipping through physical pages without an algorithm telling me what to read next. Do you still host events?&quot;
          </p>
        </div>
      </ScrollReveal>

      <ScrollReveal direction="up" delay={0.3} duration={0.9}>
        <div
          className="bg-[var(--color-surface-2)] rounded-2xl p-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-aea576">
            Events are the heartbeat of this place. We host monthly readings with local poets, seasonal book clubs, and quiet Sunday afternoon story hours. It&apos;s all about slowing down and talking to each other about what we love.
          </p>
        </div>
      </ScrollReveal>

      <FadeIn delay={0.8} duration={0.9}>
        <blockquote
          className="my-12 pl-6 border-l-2 border-[var(--color-accent)]"
          style={{ fontFamily: "var(--font-display)", fontStyle: "italic" }} data-pebble-id="pb-215ad8">
          <p className="text-xl md:text-2xl text-[var(--color-text-primary)] mb-2" data-pebble-id="pb-67fb98">
            &quot;A bookstore without conversation is just a warehouse with shelves.&quot;
          </p>
          <footer className="text-sm font-sans text-[var(--color-text-secondary)]">
            Marc Santos — Owner <sup>2</sup>
          </footer>
        </blockquote>
      </FadeIn>

      <div className="flex flex-wrap gap-4 mt-4">
        <FadeIn delay={0.6} duration={0.9}>
          <a href="tel:[BUSINESS PHONE]" className="text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-302428">
            Let&apos;s talk →
          </a>
        </FadeIn>
        <FadeIn delay={0.8} duration={0.9}>
          <a href="/faq" className="font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-405641">
            See events →
          </a>
        </FadeIn>
      </div>
    </section>
  );
}