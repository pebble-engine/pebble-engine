import Image from "next/image";
import { BRAND_NAME, EMAIL, ADDRESS, INSTAGRAM_GRID } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-[#fbf7ee] pt-24 pb-8 px-6 border-t border-[#1f1a14]/10">
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-start">
        <div>
          <p className="font-[family-name:var(--font-display)] italic text-2xl text-[#1f1a14] mb-4">
            {BRAND_NAME}
          </p>
          <p className="text-[#1f1a14]/50 text-sm leading-relaxed max-w-xs mb-6">
            Cinematic, editorial wedding photography. {ADDRESS}
          </p>
          <a href={`mailto:${EMAIL}`} className="text-[#a47236] hover:underline text-sm">
            {EMAIL}
          </a>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {INSTAGRAM_GRID.map((src, i) => (
            <div key={i} className="relative aspect-square rounded-sm overflow-hidden bg-[#1f1a14]/5">
              <Image
                src={src}
                alt={`Instagram preview ${i + 1}`}
                fill
                sizes="(max-width: 768px) 33vw, 200px"
                className="grayscale object-cover opacity-80 hover:opacity-100 transition-opacity cursor-pointer"
              />
            </div>
          ))}
          <div className="aspect-square bg-[#1f1a14]/10 flex items-center justify-center rounded-sm cursor-pointer hover:bg-[#a47236]/20 transition-colors">
            <span className="text-xs text-[#1f1a14]/60 font-medium">View Instagram</span>
          </div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-[#1f1a14]/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-[#1f1a14]/30">
        <p>© {new Date().getFullYear()} {BRAND_NAME}. All rights reserved.</p>
        <p>Designed for {BRAND_NAME} · [License # XXXXX]</p>
      </div>
    </footer>
  );
}
