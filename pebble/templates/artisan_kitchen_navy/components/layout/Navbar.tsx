"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  NAV_LINKS,
  SITE_TITLE,
  HERO_CTA_PRIMARY,
  HERO_CTA_PRIMARY_HREF,
} from "@/content/site";

/**
 * Navbar — DNA's pill_link_floating pattern.
 * Sticky liquid-glass header with rounded-full link pills, a gradient
 * Order-Now CTA pill on the right, and a translucent mobile drawer.
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
        scrolled ? "liquid-glass-strong" : "bg-transparent",
      )}
    >
      <div className="page-container flex items-center justify-between py-4 md:py-5">
        {/* Wordmark — Fraunces, slight italic for warmth */}
        <Link
          href="/"
          className="font-display text-2xl md:text-[26px] font-medium text-ink leading-none"
          aria-label={`${SITE_TITLE} — home`}
        >
          {SITE_TITLE}
        </Link>

        {/* Desktop nav — pill links */}
        <nav aria-label="Primary" className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map((link) => (
            <Link key={link.href} href={link.href} className="pill-link">
              {link.label}
            </Link>
          ))}
        </nav>

        {/* CTA + mobile menu */}
        <div className="flex items-center gap-3">
          <Link
            href={HERO_CTA_PRIMARY_HREF}
            className="hidden md:inline-flex btn-primary"
          >
            {HERO_CTA_PRIMARY}
          </Link>

          <button
            type="button"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((s) => !s)}
            className={cn(
              "md:hidden inline-flex items-center justify-center rounded-full w-11 h-11 text-ink transition-all",
              "liquid-glass",
            )}
          >
            {/* Animated burger: three bars -> X */}
            <span className="relative block h-3 w-5" aria-hidden="true">
              <span
                className={cn(
                  "absolute left-0 top-0 h-[2px] w-full bg-ink transition-all duration-300",
                  open && "translate-y-[5px] rotate-45",
                )}
              />
              <span
                className={cn(
                  "absolute left-0 top-[5px] h-[2px] w-full bg-ink transition-opacity duration-200",
                  open && "opacity-0",
                )}
              />
              <span
                className={cn(
                  "absolute left-0 top-[10px] h-[2px] w-full bg-ink transition-all duration-300",
                  open && "-translate-y-[5px] -rotate-45",
                )}
              />
            </span>
          </button>
        </div>
      </div>

      {/* Mobile sheet — liquid-glass drawer */}
      {open && (
        <div
          className="md:hidden absolute inset-x-0 top-full liquid-glass-strong border-t border-edge/60"
          role="dialog"
          aria-modal="true"
        >
          <nav aria-label="Mobile" className="page-container py-6 flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="py-3 font-display text-2xl text-ink hover:text-crust transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href={HERO_CTA_PRIMARY_HREF}
              onClick={() => setOpen(false)}
              className="btn-primary mt-3 w-full"
            >
              {HERO_CTA_PRIMARY}
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
