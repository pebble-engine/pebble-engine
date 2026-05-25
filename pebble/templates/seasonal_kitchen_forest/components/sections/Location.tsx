import { Reveal } from "@/components/ui/Reveal";
import { ADDRESS, PHONE, EMAIL, HOURS } from "@/content/site";

export function Location() {
  return (
    <section id="location" className="py-24 px-6 bg-charcoal text-bone">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-16">
        <Reveal>
          <div className="bg-bone/10 rounded-sm h-80 lg:h-full flex items-center justify-center border border-bone/20">
            <p className="text-bone/60 font-medium tracking-wide text-center px-4">[Interactive Map Placeholder]</p>
          </div>
        </Reveal>
        <div className="space-y-12">
          <Reveal>
            <h2 className="font-[family-name:var(--font-display)] text-4xl mb-6">Visit</h2>
            <address className="not-italic text-lg leading-relaxed space-y-2">
              <p>{ADDRESS}</p>
              <p>
                <a href={`tel:${PHONE}`} className="underline underline-offset-4 hover:text-warmgold transition-colors">
                  {PHONE}
                </a>
              </p>
              <p>
                <a href={`mailto:${EMAIL}`} className="underline underline-offset-4 hover:text-warmgold transition-colors">
                  {EMAIL}
                </a>
              </p>
            </address>
          </Reveal>
          <Reveal delay={0.1}>
            <h3 className="font-[family-name:var(--font-display)] text-2xl mb-4">Hours</h3>
            <table className="w-full text-base border-collapse">
              <tbody className="divide-y divide-bone/20">
                {HOURS.map((row) => (
                  <tr key={row.day}>
                    <td className="py-2">{row.day}</td>
                    <td className="text-right">{row.hours}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
