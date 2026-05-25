import { Sparkles } from "lucide-react";
import { PHILOSOPHY_QUOTE, PHILOSOPHY_AUTHOR } from "@/content/site";

export function Philosophy() {
  return (
    <section id="philosophy" className="py-32 px-6 sm:px-12 md:px-20 bg-[#0B0C0E] border-t border-white/5 relative overflow-hidden text-center">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-white/[0.01] blur-3xl pointer-events-none" />
      <div className="max-w-4xl mx-auto space-y-8 relative z-10">
        <Sparkles className="w-6 h-6 text-white/50 mx-auto" />
        <blockquote className="text-2xl sm:text-3xl md:text-4xl font-serif font-light text-slate-300 italic leading-relaxed">
          &ldquo;{PHILOSOPHY_QUOTE}&rdquo;
        </blockquote>
        <div className="w-12 h-px bg-white/20 mx-auto" />
        <p className="text-[10px] tracking-[0.3em] text-slate-500 uppercase font-sans">
          {PHILOSOPHY_AUTHOR}
        </p>
      </div>
    </section>
  );
}
