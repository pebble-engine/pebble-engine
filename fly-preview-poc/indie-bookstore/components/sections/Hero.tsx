"use client";
import Link from "next/link";
import { FadeIn } from "@/components/ui/FadeIn";

export function Hero() {
  return (
    <section
      className="relative min-h-[100dvh] flex flex-col justify-center items-center px-6 md:px-12 lg:px-16 py-24"
      style={{ background: "var(--color-bg)" }}
    >
      <div className="w-full max-w-[680px] space-y-6">
        <FadeIn delay={0.8} duration={0.9}>
          <h1 className="sr-only" data-pebble-id="pb-b542e4">
            "I've been looking for a place to discover books outside of the algorithmic bestsellers. Can you help me find something truly unique?"
          </h1>
        </FadeIn>

        <FadeIn delay={0.8} duration={0.9}>
          <div
            className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)]"
            style={{ fontFamily: "var(--font-body)" }}
          >
            <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-529f96">
              &quot;I&apos;ve been looking for a place to discover books outside of the algorithmic bestsellers. Can you help me find something truly unique?&quot;
            </p>
          </div>
        </FadeIn>

        <FadeIn delay={1.2} duration={0.9}>
          <div
            className="bg-[var(--color-surface-2)] rounded-2xl p-6 mb-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm"
            style={{ fontFamily: "var(--font-body)" }}
          >
            <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-9d97e1">
              Absolutely. We curate every shelf by hand, focusing on independent presses, Pacific Northwest authors, and titles that never see a corporate algorithm. Sit in the reading nook, grab a coffee, and let a staff member walk you through our current favorites.
            </p>
          </div>
        </FadeIn>

        <FadeIn delay={1.4} duration={0.9}>
          <p
            className="text-sm mb-6"
            style={{ fontFamily: "var(--font-body)", color: "var(--color-text-secondary)" }} data-pebble-id="pb-e977ec">
            Marc Santos — Owner since 1987
          </p>
        </FadeIn>

        <FadeIn delay={1.4} duration={0.9}>
          <div className="flex flex-wrap gap-4">
            <Link
              href="tel:[BUSINESS PHONE]"
              className="inline-flex items-center gap-2 text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent py-3 px-5 rounded-lg min-h-[44px]"
            >
              Yes, let&apos;s talk →
            </Link>
          </div>
        </FadeIn>
      </div>
    </section>
  );
}