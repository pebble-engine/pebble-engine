"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  NAV_LINKS,
  WORDMARK_EYEBROW,
  WORDMARK_MAIN,
} from "@/content/site";

/**
 * Navbar — editorial top nav.
 * Sticky white-glass nav: Pinyon Script eyebrow above tracked display wordmark,
 * horizontal link list on the right, mobile hamburger that opens a glass sheet.
 */
export function Navbar() {
  const [open, setOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll when mobile menu open
  React.useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <header
      className={cn(
        "sticky top-0 z-50 transition-all duration-300",
        scrolled ? "glass-card-strong" : "bg-transparent",
      )}
    >
      <div className="page-container flex items-center justify-between py-4 md:py-5">
        {/* Wordmark */}
        <Link
          href="/"
          className="group flex flex-col items-start leading-none"
          aria-label="Home"
        >
          <span className="font-script text-2xl md:text-[28px] text-tertiary -mb-2">
            {WORDMARK_EYEBROW}
          </span>
          <span className="font-display text-xl md:text-2xl tracking-[0.16em] uppercase text-on-surface">
            {WORDMARK_MAIN}
          </span>
        </Link>

        {/* Desktop nav */}
        <nav aria-label="Primary" className="hidden md:flex items-center gap-10">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-button text-on-surface hover:text-primary transition-colors duration-200"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Cart chip + mobile menu */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            aria-label="View cart"
            className="hidden md:inline-flex items-center gap-2 rounded-full glass-card px-4 py-2 text-xs uppercase tracking-[0.18em] text-on-surface hover:shadow-vapor transition-all"
          >
            <span aria-hidden="true">&#10070;</span>
            <span>Bag</span>
          </button>

          <button
            type="button"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((s) => !s)}
            className="md:hidden inline-flex items-center justify-center rounded-full glass-card w-11 h-11 text-on-surface"
          >
            <span aria-hidden="true" className="text-lg">
              {open ? "×" : "☰"}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile sheet */}
      {open && (
        <div
          className="md:hidden absolute inset-x-0 top-full glass-card-strong border-t border-outline-variant/50"
          role="dialog"
          aria-modal="true"
        >
          <nav aria-label="Mobile" className="page-container py-6 flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="py-3 text-display text-2xl text-on-surface hover:text-primary transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
