"use client";
import { ContactFormWarm } from "@/components/sections/ContactFormWarm";
import { FadeIn } from "@/components/ui/FadeIn";

export default function ContactPage() {
  return (
    <main className="min-h-[100dvh] flex flex-col justify-center px-6 md:px-12 py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto w-full">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-8 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-7c0171">
            Get in touch
          </h1>
        </FadeIn>
        <FadeIn delay={0.4} duration={0.9}>
          <ContactFormWarm />
        </FadeIn>
      </div>
    </main>
  );
}