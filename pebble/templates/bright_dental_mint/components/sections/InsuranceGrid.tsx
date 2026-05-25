import { Reveal } from "@/components/ui/Reveal";
import { INSURANCE_CARRIERS, HOURS } from "@/content/site";

export function InsuranceGrid() {
  return (
    <section className="bg-slate-50 border-t border-slate-100 py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <Reveal>
          <div className="text-center mb-12">
            <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold text-navy mb-3">
              Insurance &amp; Hours
            </h2>
            <p className="text-slate-600 max-w-2xl mx-auto leading-relaxed">
              We network with most major PPO plans. HMO or Medicaid? Call us — we&apos;ll help you find the right next step.
            </p>
          </div>
        </Reveal>

        <Reveal delay={0.1}>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 mb-16">
            {INSURANCE_CARRIERS.map((carrier) => (
              <div
                key={carrier}
                className="bg-white border border-slate-200 rounded-xl px-4 py-4 text-center text-sm font-semibold text-navy shadow-sm"
              >
                {carrier}
              </div>
            ))}
          </div>
        </Reveal>

        <Reveal delay={0.15}>
          <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 max-w-2xl mx-auto">
            <h3 className="font-[family-name:var(--font-display)] text-2xl font-bold text-navy mb-4">
              Office Hours
            </h3>
            <ul className="space-y-2">
              {HOURS.map((row) => (
                <li key={row.day} className="flex justify-between text-slate-600 border-b border-slate-100 last:border-b-0 py-2">
                  <span>{row.day}</span>
                  <span className="font-medium text-navy text-right">{row.hours}</span>
                </li>
              ))}
            </ul>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
