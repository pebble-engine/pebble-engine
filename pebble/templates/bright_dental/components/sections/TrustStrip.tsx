import { Reveal } from "@/components/ui/Reveal";

export function TrustStrip() {
  return (
    <section className="py-8 bg-slate-50 border-y border-slate-100">
      <Reveal>
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap items-center justify-center gap-6 md:gap-12">
          <div className="flex items-center gap-2 text-sm font-semibold text-navy">
            <svg className="w-5 h-5 text-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            We accept [Aetna] [Delta Dental] [BCBS] &amp; [+8 more]
          </div>
          <div className="w-px h-6 bg-slate-300 hidden md:block" />
          <div className="flex items-center gap-2 text-sm font-semibold text-navy">
            <span className="text-mint text-lg">★★★★★</span>
            <span>[N]+ patients trust us</span>
          </div>
          <div className="w-px h-6 bg-slate-300 hidden md:block" />
          <div className="text-sm font-semibold text-navy">[N]+ years in [City]</div>
        </div>
      </Reveal>
    </section>
  );
}
