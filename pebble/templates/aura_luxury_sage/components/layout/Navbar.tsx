"use client";

import { useState, useEffect } from "react";
import { Compass, Menu, X } from "lucide-react";
import { BRAND_NAME, NAV_LINKS } from "@/content/site";

export function Navbar() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header className="sticky top-0 z-40 w-full bg-[#0f1612]/80 backdrop-blur-md border-b border-white/5 py-5 px-6 sm:px-12 md:px-20 flex items-center justify-between">
      <a href="#" className="flex items-center space-x-2">
        <span className="w-5 h-5 rounded-full border border-white flex items-center justify-center">
          <span className="text-[9px] font-serif font-light text-white leading-none">A</span>
        </span>
        <span className="text-sm font-serif font-medium tracking-[0.35em] text-white uppercase select-none">
          {BRAND_NAME}
        </span>
      </a>

      <nav className="hidden md:flex items-center space-x-10 text-[10px] tracking-[0.2em] uppercase font-sans text-slate-400">
        {NAV_LINKS.map((link) => (
          <a key={link.href} href={link.href} className="hover:text-white transition-colors">
            {link.label}
          </a>
        ))}
      </nav>

      <div className="hidden md:block">
        <a
          href="#services"
          className="inline-flex items-center space-x-2 border border-white/10 hover:border-white/30 rounded-full px-4 py-2 bg-white/5 text-[10px] tracking-[0.15em] uppercase font-sans text-white transition-all duration-300"
        >
          <Compass className="w-3.5 h-3.5" />
          <span>Book Consultation</span>
        </a>
      </div>

      <button
        className="md:hidden p-2 text-white"
        aria-label={open ? "Close menu" : "Open menu"}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <X size={24} /> : <Menu size={24} />}
      </button>

      {open && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-[#0f1612] border-b border-white/5 px-6 py-6 flex flex-col gap-5 z-50">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[12px] tracking-[0.2em] uppercase font-sans text-slate-300 hover:text-white"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#services"
            className="inline-flex items-center justify-center border border-white/10 rounded-full px-4 py-2.5 bg-white/5 text-[11px] tracking-[0.15em] uppercase font-sans text-white"
            onClick={() => setOpen(false)}
          >
            Book Consultation
          </a>
        </div>
      )}
    </header>
  );
}
