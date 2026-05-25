import { BRAND_NAME, ADDRESS, PHONE } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-charcoal text-bone/60 py-16 px-6 border-t border-bone/10">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
        <div className="text-center md:text-left">
          <p className="font-[family-name:var(--font-display)] text-xl tracking-widest uppercase text-bone/90 mb-2">
            {BRAND_NAME}
          </p>
          <p className="text-sm">{ADDRESS} · {PHONE}</p>
        </div>
        <div className="flex gap-6">
          <a href="#" className="hover:text-warmgold transition-colors text-sm">Instagram</a>
          <a href="#" className="hover:text-warmgold transition-colors text-sm">Facebook</a>
          <a href="#" className="hover:text-warmgold transition-colors text-sm">Resy</a>
        </div>
        <p className="text-xs text-bone/30">© {new Date().getFullYear()} All rights reserved.</p>
      </div>
    </footer>
  );
}
