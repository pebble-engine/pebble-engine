import { Reveal } from "@/components/ui/Reveal";
import { SERVICES, type Service } from "@/content/site";

function Icon({ name }: { name: Service["icon"] }) {
  const common = "w-6 h-6";
  switch (name) {
    case "sparkle":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L14 21l-2-2-5.143 5.143L6 16l-4-4z" />
        </svg>
      );
    case "smile":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case "kid":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6m0 0v6m10-9a10 10 0 11-20 0 10 10 0 0120 0z" />
        </svg>
      );
    case "shine":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      );
    case "clock":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      );
    case "card":
      return (
        <svg className={common} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
          <path strokeLinecap="round" strokeLinejoin="round" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      );
  }
}

export function Services() {
  return (
    <section id="services" className="py-20 lg:py-28 px-6 bg-white">
      <div className="max-w-7xl mx-auto">
        <Reveal>
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="font-[family-name:var(--font-display)] text-3xl md:text-4xl font-bold text-navy mb-3">
              Everything your smile needs
            </h2>
            <p className="text-slate-600 leading-relaxed">
              Preventive care, gentle fillings, kids-friendly checkups, and transparent pricing. No surprise bills.
            </p>
          </div>
        </Reveal>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {SERVICES.map((s, i) => (
            <Reveal key={s.title} delay={i * 0.05}>
              <article className="hover-lift p-8 bg-white border border-slate-200 rounded-2xl shadow-sm h-full">
                <div className="w-12 h-12 bg-ice rounded-xl flex items-center justify-center mb-5 text-navy">
                  <Icon name={s.icon} />
                </div>
                <h3 className="font-[family-name:var(--font-display)] text-xl font-bold mb-2">{s.title}</h3>
                <p className="text-slate-600 leading-relaxed">{s.body}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
