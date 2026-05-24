"use client";
import Image from "next/image";
import { FadeIn } from "@/components/ui/FadeIn";
import { ScrollReveal } from "@/components/ui/ScrollReveal";

const services = [
  { title: "Curated Collections", desc: "Hand-picked literary fiction, independent presses, and Pacific Northwest authors.", img: "/images/services/curated.jpg" },
  { title: "Staff Recommendations", desc: "Real people, real tastes. Get bookish guidance that algorithms can't match.", img: "/images/services/staff.jpg" },
  { title: "Community Events", desc: "Readings, book clubs, and workshops hosted in our cozy reading nook.", img: "/images/services/events.jpg" },
];

export default function ServicesPage() {
  return (
    <main className="min-h-[100dvh] py-32" style={{ background: "var(--color-bg)" }}>
      <div className="max-w-prose mx-auto px-6 mb-24">
        <FadeIn delay={0.2} duration={0.9}>
          <h1 className="text-4xl md:text-5xl font-display italic mb-6 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-2f49e1">
            Our Services
          </h1>
          <p className="text-lg text-[var(--color-text-secondary)]" data-pebble-id="pb-5eec31">
            We don't just sell books. We cultivate reading communities.
          </p>
        </FadeIn>
      </div>

      {services.map((s, i) => (
        <section key={s.title} className={`py-24 ${i % 2 === 0 ? "bg-[var(--color-surface-1)]" : "bg-[var(--color-bg)]"}`}>
          <div className={`max-w-7xl mx-auto px-6 md:px-12 flex flex-col ${i % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse"} gap-12`}>
            <ScrollReveal direction="up" className="w-full">
              <div className="relative w-full h-[400px] overflow-hidden rounded-2xl">
                <Image src={s.img} alt={s.title} fill className="object-cover" />
              </div>
            </ScrollReveal>
            <ScrollReveal direction="up" className="flex flex-col justify-center">
              <h2 className="text-3xl font-display italic mb-4 text-[var(--color-text-primary)]" style={{ fontFamily: "var(--font-display)" }} data-pebble-id="pb-98e361">{s.title}</h2>
              <p className="text-lg text-[var(--color-text-secondary)] mb-6" data-pebble-id="pb-574aa5">{s.desc}</p>
              <a href="/contact" className="inline-flex items-center gap-2 text-[var(--color-accent)] font-medium hover:opacity-80 transition-opacity py-3 px-5 rounded-lg min-h-[44px]" data-pebble-id="pb-072642">
                Learn more →
              </a>
            </ScrollReveal>
          </div>
        </section>
      ))}
    </main>
  );
}