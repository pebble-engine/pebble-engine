import { BRAND_NAME, ADDRESS, CITY_LINE, PHONE, PHONE_TEL, EMAIL, LICENSE, BOOKING_HREF } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-navy text-slate-200 py-16 px-6 border-t border-slate-700">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12">
        <div className="md:col-span-2">
          <p className="font-[family-name:var(--font-display)] text-2xl font-bold text-white mb-3">
            {BRAND_NAME}
          </p>
          <p className="text-sm leading-relaxed max-w-xs">
            Calm, honest, kid-friendly dentistry for every age. No upsells. No pressure. Just healthy smiles.
          </p>
        </div>
        <div>
          <h4 className="font-semibold text-white mb-4">Quick Links</h4>
          <ul className="space-y-3 text-sm">
            <li><a href={BOOKING_HREF} className="hover:text-mint transition-colors">Book Now</a></li>
            <li><a href="/faq" className="hover:text-mint transition-colors">Insurance & FAQ</a></li>
            <li><a href="/team" className="hover:text-mint transition-colors">Meet the Team</a></li>
            <li><a href="#" className="hover:text-mint transition-colors">Privacy Policy</a></li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-white mb-4">Contact</h4>
          <ul className="space-y-2 text-sm">
            <li>{ADDRESS}</li>
            <li>{CITY_LINE}</li>
            <li><a href={`tel:${PHONE_TEL}`} className="hover:text-mint transition-colors">{PHONE}</a></li>
            <li><a href={`mailto:${EMAIL}`} className="hover:text-mint transition-colors">{EMAIL}</a></li>
          </ul>
        </div>
      </div>
      <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-slate-700 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-400">
        <p>Dental License #: {LICENSE} · © {new Date().getFullYear()} {BRAND_NAME}. All rights reserved.</p>
        <div className="flex gap-4 items-center">
          <a href="#" className="hover:text-white transition-colors">Instagram</a>
          <a href="#" className="hover:text-white transition-colors">Facebook</a>
          <span className="mx-1">·</span>
          <a href="#" className="hover:text-white transition-colors underline">Accessibility Statement</a>
        </div>
      </div>
    </footer>
  );
}
