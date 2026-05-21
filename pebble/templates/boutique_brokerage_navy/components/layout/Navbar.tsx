"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/cn";
import {
  NAV_LINKS,
  WORDMARK_MARK,
  WORDMARK_MAIN,
} from "@/content/site";

/**
 * Navbar — floating top nav using mix-blend-difference so the logo + links
 * invert through any background imagery beneath them. Mobile menu uses a
 * clip-path circle reveal anchored to top-right.
 */
export function Navbar() {
  const [open, setOpen] = React.useState(false);

  // Lock body scroll when mobile menu open
  React.useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.style.overflow = open ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <header className="fixed top-0 inset-x-0 z-50 mix-blend-difference text-fg">
        <div className="page-container flex items-center justify-between py-5 md:py-7">
          {/* Wordmark — brass 8x8 slab + uppercase mark. The brass
              square is inverted by mix-blend-difference but reads as a sharp
              accent against any background. */}
          <Link
            href="/"
            className="group flex items-center gap-3 leading-none"
            aria-label="Home"
          >
            <span
              aria-hidden="true"
              className="inline-flex h-8 w-8 items-center justify-center bg-accent font-display font-black text-xs text-fg"
            >
              {WORDMARK_MARK}
            </span>
            <span className="font-display font-black text-base md:text-lg uppercase tracking-tighter text-fg">
              {WORDMARK_MAIN}
            </span>
          </Link>

          {/* Desktop nav */}
          <nav aria-label="Primary" className="hidden md:flex items-center gap-10">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-button text-fg hover:text-accent transition-colors duration-200"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Mobile menu toggle */}
          <button
            type="button"
            aria-label={open ? "Close menu" : "Open menu"}
            aria-expanded={open}
            onClick={() => setOpen((s) => !s)}
            className="md:hidden inline-flex items-center justify-center w-10 h-10 border border-fg cinematic-radius text-fg"
          >
            <span aria-hidden="true" className="text-lg leading-none">
              {open ? "×" : "≡"}
            </span>
          </button>
        </div>
      </header>

      {/* Mobile overlay — full-bleed dark sheet that drops in from the top.
          We use simple opacity + translateY rather than clip-path so the
          reveal still works when prefers-reduced-motion is on. */}
      <div
        className={cn(
          "fixed inset-0 z-40 md:hidden bg-bg transition-all duration-500 ease-out",
          open
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none",
        )}
        role="dialog"
        aria-modal="true"
        aria-hidden={!open}
      >
        <div className="page-container pt-32 pb-16 h-full flex flex-col">
          <nav aria-label="Mobile" className="flex flex-col gap-4">
            {NAV_LINKS.map((link, i) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className={cn(
                  "py-4 text-display border-b border-border text-fg hover:text-accent transition-colors",
                  "transform transition-all duration-500 ease-out",
                  open
                    ? "translate-y-0 opacity-100"
                    : "translate-y-4 opacity-0",
                )}
                style={{ transitionDelay: `${i * 60}ms` }}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </>
  );
}
