"use client";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import { BRAND_NAME, NAV_LINKS } from "@/content/site";

export function Navbar() {
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header
      className={`sticky top-0 z-50 w-full bg-[#2a1810] border-b-4 border-[#d97444] transition-all duration-300 ${
        scrolled ? "py-3" : "py-4"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <a href="#" className="flex items-center gap-3">
          <span className="w-3 h-6 bg-[#d97444] inline-block" />
          <span className="font-[family-name:var(--font-display)] text-xl text-[#d97444] tracking-tight uppercase">
            {BRAND_NAME}
          </span>
        </a>

        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-[#e7e5e4]/80 hover:text-[#d97444] uppercase tracking-wide transition-colors"
            >
              {link.label}
            </a>
          ))}
          <a
            href="#estimate"
            className="btn-shimmer px-6 py-2 font-bold uppercase text-sm tracking-wide rounded-sm"
          >
            Get Estimate
          </a>
        </div>

        <button
          className="md:hidden p-2 text-[#d97444]"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden absolute top-full left-0 right-0 px-6 pb-4 pt-2 border-t border-[#e7e5e4]/10 bg-[#2a1810] flex flex-col gap-3">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="block py-2 text-sm text-[#e7e5e4]/80 hover:text-[#d97444] uppercase tracking-wide"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#estimate"
            className="btn-brick text-center text-sm uppercase font-bold rounded mt-2 py-3"
            onClick={() => setOpen(false)}
          >
            Request Estimate
          </a>
        </div>
      )}
    </header>
  );
}
