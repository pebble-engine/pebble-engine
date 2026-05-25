"use client";

import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { BRAND_NAME, NAV_LINKS, RESERVATION_HREF } from "@/content/site";

export function Navbar({ transparent = false }: { transparent?: boolean }) {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const useDark = transparent && !scrolled;

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
        useDark ? "bg-transparent pt-6 pb-4" : "bg-bone shadow-sm pt-4 pb-3"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <a
          href="/"
          className={`font-[family-name:var(--font-display)] text-xl tracking-widest uppercase ${useDark ? "text-bone" : "text-charcoal"}`}
        >
          {BRAND_NAME}
        </a>
        <div className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className={`text-sm tracking-wide ${useDark ? "text-bone hover:text-warmgold" : "text-charcoal hover:text-burgundy"} transition-colors`}
            >
              {link.label}
            </a>
          ))}
          <a
            href={RESERVATION_HREF}
            className="bg-burgundy text-bone px-6 py-2 rounded-full text-sm font-medium tracking-wide hover:bg-charcoal transition-colors"
          >
            Reserve a Table
          </a>
        </div>
        <button
          className={`md:hidden p-2 ${useDark ? "text-bone" : "text-charcoal"}`}
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-bone border-t border-charcoal/10 px-6 py-6 flex flex-col gap-4 shadow-lg">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-base text-charcoal"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href={RESERVATION_HREF}
            className="bg-burgundy text-bone px-6 py-3 rounded-full text-sm font-medium tracking-wide text-center"
            onClick={() => setOpen(false)}
          >
            Reserve a Table
          </a>
        </div>
      )}
    </header>
  );
}
