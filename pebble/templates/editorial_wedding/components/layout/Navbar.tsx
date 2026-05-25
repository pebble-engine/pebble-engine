"use client";

import { useEffect, useState } from "react";
import { BRAND_NAME, NAV_LINKS } from "@/content/site";
import { Menu, X } from "lucide-react";

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
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        scrolled ? "bg-[#0a0a0a]/90 backdrop-blur-md pt-3 pb-3 border-b border-[#f5f1e8]/10" : "pt-6 pb-4"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <a href="#" className="font-[family-name:var(--font-display)] text-xl italic font-semibold tracking-wide text-[#f5f1e8]">
          {BRAND_NAME}
        </a>
        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-[#f5f1e8]/80 hover:text-[#b08d57] transition-colors relative after:absolute after:left-0 after:-bottom-1 after:w-0 after:h-px after:bg-[#b08d57] after:transition-all hover:after:w-full"
            >
              {link.label}
            </a>
          ))}
          <a
            href="#inquiry"
            className="font-[family-name:var(--font-display)] italic text-lg text-[#b08d57] hover:text-[#f5f1e8] transition-colors"
          >
            Inquire
          </a>
        </div>
        <button
          className="md:hidden p-2 text-[#f5f1e8]"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden bg-[#0a0a0a]/95 backdrop-blur border-t border-[#f5f1e8]/10 px-6 py-4">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="block py-3 text-[#f5f1e8]/80 hover:text-[#b08d57]"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href="#inquiry"
            className="block py-3 font-[family-name:var(--font-display)] italic text-[#b08d57] text-lg"
            onClick={() => setOpen(false)}
          >
            Inquire
          </a>
        </div>
      )}
    </header>
  );
}
