import { ADDRESS, CITY_LINE, PHONE, PHONE_TEL, HOURS } from "@/content/site";

export function BookingSidebar() {
  return (
    <div className="space-y-8">
      <div className="bg-slate-100 rounded-2xl aspect-[4/3] flex items-center justify-center border border-slate-200">
        <div className="text-center p-6 text-slate-500">
          <svg className="w-12 h-12 mx-auto mb-4 text-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
            <path strokeLinecap="round" strokeLinejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.828 0l-4.24-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p className="font-semibold mb-1 text-navy">{ADDRESS}, {CITY_LINE}</p>
          <a href={`tel:${PHONE_TEL}`} className="text-coral hover:underline font-medium">Call us: {PHONE}</a>
          <p className="mt-4 text-sm">[Embed Google Maps iframe here for turn-by-turn.]</p>
        </div>
      </div>
      <div className="space-y-2">
        <h3 className="font-[family-name:var(--font-display)] text-xl font-bold text-navy">Office Hours</h3>
        <ul className="space-y-2 text-slate-600">
          {HOURS.map((row) => (
            <li key={row.day} className="flex justify-between">
              <span>{row.day}</span>
              <span className="font-medium text-navy text-right">{row.hours}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
