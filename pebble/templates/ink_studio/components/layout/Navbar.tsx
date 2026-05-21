"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  NAV_LINKS,
  WORDMARK_MAIN,
  WORDMARK_SECOND,
} from "@/content/site";

/**
 * Navbar — floating header that turns black-with-backdrop-blur after 50px
 * scroll (DNA `transparent_to_solid_on_scroll`). Gold underline animates
 * under hover links.
 */
export function Navbar() {
  const [open, setOpen] = React.useState(false);
  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
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
        "fixed top-0 inset-x-0 z-50 transition-all duration-500",
        scrolled
          ? "bg-ink-bg/85 backdrop-blur-xl border-b border-ink-border/60"
          : "bg-transparent",
      )}
    >
      <div className="page-container flex items-center justify-between py-5 md:py-6">
        {/* Wordmark — blackletter */}
        <Link
          href="/"
          className="flex items-baseline gap-2 leading-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-primary"
          aria-label="Home"
        >
          <span className="font-display text-2xl md:text-[28px] text-ink-fg">
            {WORDMARK_MAIN}
          </span>
          <span className="font-display text-xl md:text-2xl text-ink-primary">
            {WORDMARK_SECOND}
          </span>
        </Link>

        {/* Desktop nav */}
        <nav aria-label="Primary" className="hidden md:flex items-center gap-10">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group relative text-button text-ink-fg hover:text-ink-primary transition-colors duration-200"
            >
              {link.label}
              <span
                aria-hidden="true"
                className="absolute -bottom-2 left-0 right-0 h-px bg-ink-primary scale-x-0 group-hover:scale-x-100 origin-left transition-transform duration-300"
              />
            </Link>
          ))}
        </nav>

        {/* Mobile menu trigger */}
        <button
          type="button"
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
          onClick={() => setOpen((s) => !s)}
          className="md:hidden inline-flex items-center justify-center border border-ink-border w-11 h-11 text-ink-fg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink-primary"
        >
          <span aria-hidden="true" className="text-lg">
            {open ? "×" : "☰"}
          </span>
        </button>
      </div>

      {/* Mobile sheet */}
      {open && (
        <div
          className="md:hidden absolute inset-x-0 top-full bg-ink-bg/95 backdrop-blur-xl border-t border-ink-border"
          role="dialog"
          aria-modal="true"
        >
          <nav aria-label="Mobile" className="page-container py-6 flex flex-col gap-2">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="py-3 font-display text-3xl text-ink-fg hover:text-ink-primary transition-colors"
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
