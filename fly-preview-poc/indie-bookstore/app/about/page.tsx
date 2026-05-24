"use client";
import Image from "next/image";
import { FadeIn } from "@/components/ui/FadeIn";

export default function AboutPage() {
  return (
    <main className="min-h-[100dvh] py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto px-6">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-8 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-0d3299">
            Our Story
          </h1>
        </FadeIn>
        
        <div className="relative w-full h-[300px] md:h-[500px] mb-12 overflow-hidden rounded-2xl">
          <Image src="/images/about/owner.jpg" alt="Marc Santos in the bookstore" fill className="object-cover" />
        </div>

        <FadeIn delay={0.4} duration={0.9}>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed mb-6" data-pebble-id="pb-477014">
            Founded in 1987, Indie Bookstore started as a single shelf in a downtown Portland laneway. Marc Santos, a lifelong librarian and reader, believed that book discovery should feel like a conversation, not a transaction.
          </p>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed mb-6" data-pebble-id="pb-0db78e">
            Today, we&apos;re proud to be independently owned and operated, partnering with local authors, independent publishers, and community organizations to keep literary culture alive in the Pacific Northwest.
          </p>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed" data-pebble-id="pb-fd58d0">
            We don&apos;t chase trends. We chase stories that matter. Come sit a while.
          </p>
        </FadeIn>
      </div>
    </main>
  );
}