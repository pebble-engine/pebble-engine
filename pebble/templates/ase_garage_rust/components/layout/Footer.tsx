import { BRAND_NAME, FOOTER_LINE, FOOTER_LEGAL } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-[#2a1810] py-12 px-6 border-t-4 border-[#e7e5e4]/20">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
        <div className="text-center md:text-left">
          <p className="font-[family-name:var(--font-display)] text-xl text-[#d97444] uppercase">
            {BRAND_NAME}
          </p>
          <p className="text-xs text-[#e7e5e4]/50 mt-2">{FOOTER_LINE}</p>
        </div>
        <div className="flex gap-2">
          <div className="w-8 h-8 bg-[#e7e5e4]/10 rounded-sm" />
          <div className="w-8 h-8 bg-[#e7e5e4]/10 rounded-sm" />
          <div className="w-8 h-8 bg-[#e7e5e4]/10 rounded-sm" />
        </div>
        <div className="flex gap-4 text-xs uppercase tracking-wider">
          <a href="#" className="text-[#e7e5e4]/70 hover:text-[#d97444]">Facebook</a>
          <span className="text-[#e7e5e4]/30">/</span>
          <a href="#" className="text-[#e7e5e4]/70 hover:text-[#d97444]">Google Business</a>
          <span className="text-[#e7e5e4]/30">/</span>
          <a href="#" className="text-[#e7e5e4]/70 hover:text-[#d97444]">Accessibility</a>
        </div>
      </div>
      <p className="text-center text-[10px] text-[#e7e5e4]/30 mt-8 uppercase tracking-[0.2em]">
        {FOOTER_LEGAL}
      </p>
    </footer>
  );
}
