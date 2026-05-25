"use client";

import { useEffect, useState } from "react";
import { Menu, X } from "lucide-react";
import { BRAND_NAME, NAV_LINKS, BOOKING_HREF } from "@/content/site";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled ? "bg-white/95 backdrop-blur-sm shadow-soft pt-3 pb-3" : "bg-white pt-5 pb-4"
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 flex items-center justify-between">
        <a
          href="/"
          className="font-[family-name:var(--font-display)] text-2xl tracking-tight font-bold text-navy"
        >
          {BRAND_NAME}
        </a>
        <div className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-slate-600 hover:text-navy transition-colors"
            >
              {link.label}
            </a>
          ))}
          <a
            href={BOOKING_HREF}
            className="btn-coral text-sm shadow-soft !py-2 !px-5"
          >
            Book Appointment
          </a>
        </div>
        <button
          className="md:hidden p-2 text-navy hover:bg-slate-50 rounded-lg transition"
          aria-label={open ? "Close menu" : "Open menu"}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {open && (
        <div className="md:hidden absolute top-full left-0 right-0 bg-white border-t border-slate-100 px-6 pt-4 pb-6 shadow-lg">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="block py-3 text-base font-medium text-navy hover:bg-slate-50 rounded-lg transition px-2"
              onClick={() => setOpen(false)}
            >
              {link.label}
            </a>
          ))}
          <a
            href={BOOKING_HREF}
            className="block mt-4 text-center btn-coral"
            onClick={() => setOpen(false)}
          >
            Book Appointment
          </a>
        </div>
      )}
    </header>
  );
}
