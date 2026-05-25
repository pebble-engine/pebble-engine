import { Reveal } from "@/components/ui/Reveal";
import { TESTIMONIALS } from "@/content/site";

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 px-6 bg-[#0a0a0a] border-t border-[#f5f1e8]/10">
      <div className="max-w-4xl mx-auto space-y-16">
        {TESTIMONIALS.map((t, i) => (
          <Reveal key={i} delay={i * 0.1}>
            <p className="font-[family-name:var(--font-display)] italic text-xl md:text-2xl text-[#b08d57] leading-relaxed mb-4">
              &ldquo;{t.quote}&rdquo;
            </p>
            <p className="text-[#f5f1e8]/60 text-sm uppercase tracking-widest">— {t.author}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
