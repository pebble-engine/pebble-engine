"use client";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

export function QaServices1() {
  return (
    <section className="max-w-prose mx-auto px-6 md:px-12 py-24 md:py-32">
      <FadeIn delay={0.2} duration={0.9}>
        <h2
          className="font-display italic text-[4rem] leading-none text-[var(--color-text-muted)] mb-8"
          style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-07494d">
          I.
        </h2>
      </FadeIn>

      <ScrollReveal direction="up" delay={0.1} duration={0.9}>
        <div
          className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)] mb-6"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-980c0e">
            &quot;How do you choose what to stock? I don&apos;t want just whatever is trending on social media.&quot;
          </p>
        </div>
      </ScrollReveal>

      <ScrollReveal direction="up" delay={0.3} duration={0.9}>
        <div
          className="bg-[var(--color-surface-2)] rounded-2xl p-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-376ace">
            Every title is hand-selected by our team of readers. We prioritize literary fiction from independent presses, local Oregon voices, and rare poetry collections. If a book hasn&apos;t earned a spot on our shelves through genuine passion, it won&apos;t be here.
          </p>
        </div>
      </ScrollReveal>

      <FadeIn delay={0.8} duration={0.9}>
        <blockquote
          className="my-12 pl-6 border-l-2 border-[var(--color-accent)]"
          style={{ fontFamily: "var(--font-display)", fontStyle: "italic" }} data-pebble-id="pb-472ca6">
          <p className="text-xl md:text-2xl text-[var(--color-text-primary)] mb-2" data-pebble-id="pb-13495f">
            &quot;We don&apos;t follow algorithms. We follow curiosity.&quot;
          </p>
          <footer className="text-sm font-sans text-[var(--color-text-secondary)]">
            Sarah Chen — Head Buyer <sup>1</sup>
          </footer>
        </blockquote>
      </FadeIn>

      <div className="flex flex-wrap gap-4 mt-4">
        <FadeIn delay={0.6} duration={0.9}>
          <a href="tel:[BUSINESS PHONE]" className="text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-cc21c9">
            Let&apos;s talk →
          </a>
        </FadeIn>
        <FadeIn delay={0.8} duration={0.9}>
          <a href="/services" className="font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-2a7d7d">
            View collections →
          </a>
        </FadeIn>
      </div>
    </section>
  );
}