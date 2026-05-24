"use client";

import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import { SITE_TITLE, NAV_LINKS } from "@/content/site";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header
      className={`sticky top-0 z-50 w-full bg-white border-b border-[var(--color-border)] transition-all duration-300 ${
        scrolled ? "backdrop-blur-sm bg-white/90" : ""
      }`}
      style={{ height: 72 }}
    >
      <nav className="max-w-6xl mx-auto px-8 h-full flex items-center justify-between">
        {/* Wordmark */}
        <a
          href="/"
          className="font-[family-name:var(--font-display)] text-[18px] uppercase text-[var(--color-text-primary)] tracking-tight"
        >
          {SITE_TITLE}
        </a>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[14px] font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
            >
              {link.label}
            </a>
          ))}
          <a
            href="/contact"
            className="inline-flex items-center justify-center h-10 px-5 rounded-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-dark)] text-white text-[14px] font-semibold transition-colors"
          >
            Get a quote
          </a>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-2 text-[var(--color-text-primary)]"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {/* Mobile drawer */}
      {open && (
        <div className="md:hidden absolute top-[72px] left-0 right-0 bg-white border-b border-[var(--color-border)] px-8 py-6 flex flex-col gap-5 shadow-lg z-50">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[16px] font-medium text-[var(--color-text-primary)]"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href="/contact"
            className="inline-flex items-center justify-center h-12 px-6 rounded-full bg-[var(--color-accent)] hover:bg-[var(--color-accent-dark)] text-white text-[15px] font-semibold transition-colors"
            onClick={() => setOpen(false)}
          >
            Get a quote
          </a>
        </div>
      )}
    </header>
  );
}
