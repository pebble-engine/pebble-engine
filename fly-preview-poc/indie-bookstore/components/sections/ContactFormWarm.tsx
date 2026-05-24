"use client";
import { FadeIn } from "@/components/ui/FadeIn";
import { ContactForm } from "@/components/forms/ContactForm";

export function ContactFormWarm() {
  return (
    <section className="max-w-prose mx-auto px-6 md:px-12 py-24 md:py-32">
      <FadeIn delay={0.2} duration={0.9}>
        <h2 className="font-display italic text-[4rem] leading-none text-[var(--color-text-muted)] mb-8" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-f3a64a">
          VI.
        </h2>
      </FadeIn>

      <FadeIn delay={0.4} duration={0.9}>
        <div className="bg-[var(--color-surface-1)] rounded-2xl p-6 mb-4 ml-auto shadow-sm border border-[var(--color-border)] mb-6" style={{ fontFamily: "var(--font-body)" }}>
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-2a53f3">
            &quot;I&apos;d love to host a small reading or book club here. How do we get started?&quot;
          </p>
        </div>
      </FadeIn>

      <FadeIn delay={0.6} duration={0.9}>
        <div className="bg-[var(--color-surface-2)] rounded-2xl p-6 ml-auto border-l-4 border-[var(--color-accent)] shadow-sm mb-12" style={{ fontFamily: "var(--font-body)" }}>
          <p className="text-base md:text-lg leading-relaxed text-[var(--color-text-primary)]" data-pebble-id="pb-c3f487">
            We&apos;d love to host you. Drop us a note with your ideas, and we&apos;ll find a perfect spot in our calendar. No event is too small — even a quiet Sunday afternoon reading counts.
          </p>
        </div>
      </FadeIn>

      <FadeIn delay={0.8} duration={0.9}>
        <h3 className="text-2xl font-display italic mb-8" style={{ fontFamily: "var(--font-display)", color: "var(--color-text-primary)" }} data-pebble-id="pb-79e8bf">
          Write to us
        </h3>
        <ContactForm />
      </FadeIn>
    </section>
  );
}