"use client";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

const faqs = [
  { q: "Do you offer curbside pickup?", a: "Yes. Order online and choose curbside pickup at checkout. We'll bring your books straight to your car." },
  { q: "Can I return a book I've already read?", a: "We offer a 14-day return policy on undamaged items with a receipt. We want you to love what you read." },
  { q: "Do you ship internationally?", a: "Currently, we only ship within the United States to keep shipping costs fair and reduce our carbon footprint." },
  { q: "How do you select your staff picks?", a: "Our staff pick up from independent presses, local Oregon authors, and obscure poetry collections. If a book moves us, it goes on the shelf." },
  { q: "Can I host a book signing here?", a: "Absolutely. We host readings, book clubs, and author events regularly. Contact us to reserve a date." },
  { q: "Do you buy used books?", a: "We accept gently used literary fiction, poetry, and local history books for trade-in credit." },
];

export default function FAQPage() {
  return (
    <main className="min-h-[100dvh] py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto px-6">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-12 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-73c4f4">
            Frequently Asked Questions
          </h1>
        </FadeIn>

        <div className="space-y-8">
          {faqs.map((faq, i) => (
            <ScrollReveal key={i} direction="up" delay={i * 0.1}>
              <div className="border-b border-[var(--color-border)] pb-8">
                <h3 className="text-xl text-[var(--color-text-primary)] mb-3" data-pebble-id="pb-d22b7d">{faq.q}</h3>
                <p className="text-base text-[var(--color-text-secondary)] leading-relaxed" data-pebble-id="pb-dd808d">{faq.a}</p>
              </div>
            </ScrollReveal>
          ))}
        </div>

        <FadeIn delay={0.8} duration={0.9}>
          <div className="mt-16 p-8 bg-[var(--color-surface-1)] rounded-2xl border border-[var(--color-border)]">
            <h3 className="text-2xl font-display italic mb-4 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-f06fce">Still have questions?</h3>
            <p className="text-[var(--color-text-secondary)] mb-6" data-pebble-id="pb-060a2d">We're happy to help. Drop us a line or stop by the store.</p>
            <a href="/contact" className="inline-flex items-center gap-2 text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-6a9115">
              Get in touch →
            </a>
          </div>
        </FadeIn>
      </div>
    </main>
  );
}