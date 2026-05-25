import Image from "next/image";
import { BRAND_NAME, EMAIL, ADDRESS, INSTAGRAM_GRID } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-[#0a2820] pt-24 pb-8 px-6 border-t border-[#f5f0dc]/10">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-start">
        <div>
          <p className="font-[family-name:var(--font-display)] italic text-2xl text-[#f5f0dc] mb-4">
            {BRAND_NAME}
          </p>
          <p className="text-[#f5f0dc]/50 text-sm leading-relaxed max-w-xs mb-6">
            Cinematic, editorial wedding photography. {ADDRESS}
          </p>
          <a href={`mailto:${EMAIL}`} className="text-[#c9a96e] hover:underline text-sm">
            {EMAIL}
          </a>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {INSTAGRAM_GRID.map((src, i) => (
            <div key={i} className="relative aspect-square rounded-sm overflow-hidden bg-[#f5f0dc]/5">
              <Image
                src={src}
                alt={`Instagram preview ${i + 1}`}
                fill
                sizes="(max-width: 768px) 33vw, 200px"
                className="grayscale object-cover opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
              />
            </div>
          ))}
          <div className="aspect-square bg-[#f5f0dc]/10 flex items-center justify-center rounded-sm cursor-pointer hover:bg-[#c9a96e]/20 transition-colors">
            <span className="text-xs text-[#f5f0dc]/60 font-medium">View Instagram</span>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-[#f5f0dc]/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-[#f5f0dc]/30">
        <p>© {new Date().getFullYear()} {BRAND_NAME}. All rights reserved.</p>
        <p>Designed for {BRAND_NAME} · [License # XXXXX]</p>
      </div>
    </footer>
  );
}
