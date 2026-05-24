"use client";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

export function QaProcess() {
  return (
    <section className="max-w-prose mx-auto px-6 md:px-12 py-24 md:py-32">
      <FadeIn delay={0.2} duration={0.9}>
        <h2
          className="font-display italic text-[4rem] leading-none text-[var(--color-text-muted)] mb-8"
          style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-9ea121">
          III.
        </h2>
      </FadeIn>

      <ScrollReveal direction="up" delay={0.1} duration={0.9}>
        <div
          className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)] mb-6"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-a217ca">
            &quot;I prefer shopping in person, but sometimes I need quick delivery. How does your ordering process work?&quot;
          </p>
        </div>
      </ScrollReveal>

      <ScrollReveal direction="up" delay={0.3} duration={0.9}>
        <div
          className="bg-[var(--color-surface-2)] rounded-2xl p-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-8432e3">
            We offer BOPIS (Buy Online, Pick Up In-Store) and local curbside delivery for Portland neighbors. For wider shipping, we partner with slow-ship carriers that prioritize packaging over speed. Every book arrives wrapped in recycled paper because presentation matters.
          </p>
        </div>
      </ScrollReveal>

      <FadeIn delay={0.8} duration={0.9}>
        <blockquote
          className="my-12 pl-6 border-l-2 border-[var(--color-accent)]"
          style={{ fontFamily: "var(--font-display)", fontStyle: "italic" }} data-pebble-id="pb-d758e5">
          <p className="text-xl md:text-2xl text-[var(--color-text-primary)] mb-2" data-pebble-id="pb-68dcde">
            &quot;Take your time. The shelves aren&apos;t going anywhere.&quot;
          </p>
          <footer className="text-sm font-sans text-[var(--color-text-secondary)]">
            Indie Bookstore Team <sup>3</sup>
          </footer>
        </blockquote>
      </FadeIn>

      <div className="flex flex-wrap gap-4 mt-4">
        <FadeIn delay={0.6} duration={0.9}>
          <a href="tel:[BUSINESS PHONE]" className="text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-0c8a96">
            Let&apos;s talk →
          </a>
        </FadeIn>
        <FadeIn delay={0.8} duration={0.9}>
          <a href="/contact" className="font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-f6df61">
            Ask us more →
          </a>
        </FadeIn>
      </div>
    </section>
  );
}