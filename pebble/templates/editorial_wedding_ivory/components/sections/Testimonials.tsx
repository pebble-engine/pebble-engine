import { Reveal } from "@/components/ui/Reveal";
import { TESTIMONIALS } from "@/content/site";

export function Testimonials() {
  return (
    <section id="testimonials" className="py-24 px-6 bg-[#fbf7ee] border-t border-[#1f1a14]/10">
      <div className="max-w-4xl mx-auto space-y-16">
        {TESTIMONIALS.map((t, i) => (
          <Reveal key={i} delay={i * 0.1}>
            <p className="font-[family-name:var(--font-display)] italic text-xl md:text-2xl text-[#a47236] leading-relaxed mb-4">
              &ldquo;{t.quote}&rdquo;
            </p>
            <p className="text-[#1f1a14]/60 text-sm uppercase tracking-widest">— {t.author}</p>
          </Reveal>
        ))}
      </div>
    </section>
  );
}
