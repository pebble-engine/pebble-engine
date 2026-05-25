import { Reveal } from "@/components/ui/Reveal";
import { HOURS, ADDRESS, PHONE, SHOP_BADGES } from "@/content/site";

export function Location() {
  return (
    <section id="location" className="py-20 px-6 bg-[#facc15] text-[#1e293b]">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        <Reveal>
          <div className="space-y-6">
            <h2 className="font-[family-name:var(--font-display)] text-5xl uppercase tracking-tight mb-2">
              Shop Hours
            </h2>
            <table className="w-full text-base border-collapse">
              <tbody className="divide-y divide-[#1e293b]/20">
                {HOURS.map((row) => (
                  <tr key={row.days} className="py-3 border-b-2 border-[#1e293b]/10">
                    <td className="pr-4 py-2 font-bold">{row.days}</td>
                    <td className={`text-right font-bold ${row.closed ? "uppercase text-[#b91c1c]" : ""}`}>
                      {row.hours}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p className="text-sm font-bold mt-4">Address: {ADDRESS}</p>
            <div className="flex flex-wrap gap-4 text-xs font-bold uppercase tracking-wider">
              {SHOP_BADGES.map((b) => (
                <span key={b} className="bg-[#1e293b] text-[#facc15] px-3 py-1 rounded-sm">
                  {b}
                </span>
              ))}
            </div>
          </div>
        </Reveal>
        <Reveal>
          <div className="bg-[#e7e5e4]/50 aspect-square md:aspect-video rounded-sm flex items-center justify-center border-4 border-[#1e293b]/20 relative overflow-hidden">
            <div className="text-center p-6 z-10 bg-[#1e293b]/90 px-8 py-6">
              <svg className="w-12 h-12 mx-auto mb-3 text-[#facc15]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.24-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <p className="font-[family-name:var(--font-display)] text-lg uppercase text-[#fafaf9]">
                [Embed Google Maps Iframe Here]
              </p>
              <a href={`tel:${PHONE}`} className="block mt-2 text-[#b91c1c] hover:underline font-bold">
                {PHONE} · [24/7 Towing Line]
              </a>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
