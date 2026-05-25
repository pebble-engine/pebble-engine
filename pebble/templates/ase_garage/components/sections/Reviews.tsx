import { Reveal } from "@/components/ui/Reveal";
import { REVIEWS, REVIEWS_FOOTNOTE } from "@/content/site";

export function Reviews() {
  return (
    <section id="reviews" className="py-20 px-6 bg-[#e7e5e4]/20">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-12 gap-4">
          <Reveal>
            <h2 className="font-[family-name:var(--font-display)] text-3xl uppercase tracking-tight">
              What Drivers Say
            </h2>
          </Reveal>
          <Reveal>
            <p className="text-sm text-[#1e293b]/60 uppercase tracking-wider">{REVIEWS_FOOTNOTE}</p>
          </Reveal>
        </div>
        <div className="grid md:grid-cols-2 gap-6">
          {REVIEWS.map((r, i) => (
            <Reveal key={i} delay={0.05 * i}>
              <div className="p-6 bg-[#fafaf9] border border-[#e7e5e4] flex flex-col justify-between h-full">
                <div>
                  <div className="text-[#facc15] text-xl mb-2">★★★★★</div>
                  <p className="text-sm leading-relaxed mb-4">&ldquo;{r.quote}&rdquo;</p>
                </div>
                <p className="text-xs uppercase tracking-wider text-[#1e293b]/50">— {r.author}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
