import { MapPin, PhoneCall } from "lucide-react";
import {
  BRAND_NAME,
  EMAIL,
  PHONE,
  LOCATIONS,
  FOOTER_BODY,
  FOOTER_COMPLIANCE,
  FOOTER_RESPONSE,
} from "@/content/site";

export function Footer() {
  return (
    <footer id="inquire" className="bg-[#0f1612] border-t border-white/5 py-16 px-6 sm:px-12 md:px-20">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-12 border-b border-white/5 pb-12 mb-12">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <div className="w-5 h-5 rounded-full border border-white flex items-center justify-center">
              <span className="text-[9px] font-serif font-light text-white leading-none">A</span>
            </div>
            <span className="text-sm font-serif font-medium tracking-[0.35em] text-white uppercase">
              {BRAND_NAME}
            </span>
          </div>
          <p className="text-xs text-slate-500 font-light leading-relaxed max-w-xs">
            {FOOTER_BODY}
          </p>
        </div>

        <div className="space-y-4">
          <h4 className="text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans font-medium">Locations</h4>
          <ul className="space-y-2.5 text-xs text-slate-500 font-light font-sans">
            {LOCATIONS.map((loc) => (
              <li key={loc} className="flex items-center space-x-2">
                <MapPin className="w-3.5 h-3.5 text-slate-600 stroke-[1]" />
                <span>{loc}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="space-y-4">
          <h4 className="text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans font-medium">Concierge</h4>
          <ul className="space-y-2.5 text-xs text-slate-500 font-light font-sans">
            <li className="flex items-center space-x-2">
              <PhoneCall className="w-3.5 h-3.5 text-slate-600 stroke-[1]" />
              <span>{PHONE}</span>
            </li>
            <li>
              <a href={`mailto:${EMAIL}`} className="hover:text-white transition-colors">
                {EMAIL}
              </a>
            </li>
            <li>
              <span className="text-[10px] text-slate-600">{FOOTER_RESPONSE}</span>
            </li>
          </ul>
        </div>

        <div className="space-y-4">
          <h4 className="text-[10px] tracking-[0.2em] uppercase text-slate-400 font-sans font-medium">Compliance</h4>
          <p className="text-[11px] text-slate-500 font-light leading-relaxed">
            {FOOTER_COMPLIANCE}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-[10px] tracking-wider text-slate-600 font-sans gap-4">
        <p>© {new Date().getFullYear()} {BRAND_NAME} Pristine Services. All rights reserved.</p>
        <div className="flex space-x-6">
          <a href="#" className="hover:text-slate-400 transition-colors">Privacy Policy</a>
          <a href="#" className="hover:text-slate-400 transition-colors">Terms of Protocol</a>
          <a href="#" className="hover:text-slate-400 transition-colors">Security Clearance</a>
        </div>
      </div>
    </footer>
  );
}
