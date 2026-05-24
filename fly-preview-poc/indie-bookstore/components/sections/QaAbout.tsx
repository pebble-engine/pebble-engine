"use client";
import Image from "next/image";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

export function QaAbout() {
  return (
    <section className="max-w-prose mx-auto px-6 md:px-12 py-24 md:py-32">
      <FadeIn delay={0.2} duration={0.9}>
        <h2
          className="font-display italic text-[4rem] leading-none text-[var(--color-text-muted)] mb-8"
          style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-1648e6">
          IV.
        </h2>
      </FadeIn>

      <ScrollReveal direction="up" delay={0.1} duration={0.9}>
        <div
          className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)] mb-6"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-87448f">
            &quot;Who actually runs this place? I want to know the human behind the counter.&quot;
          </p>
        </div>
      </ScrollReveal>

      <ScrollReveal direction="up" delay={0.3} duration={0.9}>
        <div
          className="bg-[var(--color-surface-2)] rounded-2xl p-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm mb-12"
          style={{ fontFamily: "var(--font-body)" }}
        >
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-d2bde4">
            I&apos;m Marc Santos. I opened the doors in 1987 with nothing but a loan, a cart of secondhand literary fiction, and a stubborn belief that Portland deserved a place where strangers could bond over a dog-eared paperback. We&apos;re still independent, still small, and still picking every book by hand.
          </p>
        </div>
      </ScrollReveal>

      <FadeIn delay={0.8} duration={0.9}>
        <blockquote
          className="my-12 pl-6 border-l-2 border-[var(--color-accent)]"
          style={{ fontFamily: "var(--font-display)", fontStyle: "italic" }} data-pebble-id="pb-adc4e6">
          <p className="text-xl md:text-2xl text-[var(--color-text-primary)] mb-2" data-pebble-id="pb-d6dc35">
            &quot;Books are quiet, but the conversations they start are anything but.&quot;
          </p>
          <footer className="text-sm font-sans text-[var(--color-text-secondary)]">
            Marc Santos — Founder <sup>4</sup>
          </footer>
        </blockquote>
      </FadeIn>

      <div className="flex flex-wrap gap-4 mt-4">
        <FadeIn delay={0.6} duration={0.9}>
          <a href="tel:[BUSINESS PHONE]" className="text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-d83d4b">
            Let&apos;s talk →
          </a>
        </FadeIn>
        <FadeIn delay={0.8} duration={0.9}>
          <a href="/about" className="font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-dd0711">
            Read our story →
          </a>
        </FadeIn>
      </div>
    </section>
  );
}