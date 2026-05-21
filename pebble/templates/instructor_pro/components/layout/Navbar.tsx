"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";
import { Button } from "@/components/ui/Button";
import { NAV_LINKS, SITE_TITLE } from "@/content/site";

/**
 * Glassmorphism header per training_authority DNA: transparent at top,
 * gains glass + border on scroll. Pill-shaped nav links with red-tinted
 * hover bg. Bold gold SIGN UP CTA on the right. Animated 3-bar hamburger
 * on mobile.
 */
export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [drawerOpen]);

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-0 z-50 transition-all duration-300",
        scrolled ? "py-2" : "py-4",
      )}
    >
      <nav
        className={cn(
          "mx-auto flex max-w-6xl items-center justify-between gap-4 rounded-full border px-4 sm:px-5 py-2.5 transition-all duration-300",
          scrolled
            ? "border-border bg-card/85 backdrop-blur-xl shadow-lg shadow-black/30"
            : "border-transparent bg-card/40 backdrop-blur-md",
        )}
      >
        {/* Logo wordmark */}
        <Link
          href="/"
          className="flex items-center gap-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent rounded-full"
        >
          <span className="relative inline-flex h-8 w-8 items-center justify-center rounded-md border border-accent/50 bg-accent/15">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent" aria-hidden="true">
              <path d="M20 6 9 17l-5-5" />
            </svg>
          </span>
          <span className="font-display text-base font-extrabold uppercase tracking-wide-12 text-fg">
            {SITE_TITLE}
          </span>
        </Link>

        {/* Desktop links — pill-shaped per DNA */}
        <ul className="hidden items-center gap-1 md:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="rounded-full px-3.5 py-1.5 text-xs font-bold uppercase tracking-wide-15 text-fg/80 hover:bg-accent/15 hover:text-accent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right cluster — gold Sign Up CTA per DNA */}
        <div className="flex items-center gap-2 sm:gap-3">
          <Button href="/contact" size="sm" variant="gold" className="hidden sm:inline-flex">
            Sign Up
          </Button>
          <button
            type="button"
            aria-label="Open menu"
            aria-expanded={drawerOpen}
            onClick={() => setDrawerOpen((v) => !v)}
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card/40 text-fg/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          >
            <BurgerIcon open={drawerOpen} />
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      <div
        className={cn(
          "fixed inset-0 z-40 md:hidden transition-opacity duration-300",
          drawerOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none",
        )}
        onClick={() => setDrawerOpen(false)}
        aria-hidden={!drawerOpen}
      >
        <div className="absolute inset-0 bg-bg/90 backdrop-blur-xl" />
        <div
          className={cn(
            "absolute inset-x-0 top-20 mx-4 rounded-2xl border border-border bg-card/95 p-6 transition-transform duration-300",
            drawerOpen ? "translate-y-0" : "-translate-y-4",
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="block rounded-xl px-4 py-3 text-sm font-bold uppercase tracking-wide-15 text-fg hover:bg-accent/15 hover:text-accent"
                  onClick={() => setDrawerOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
          <Button
            href="/contact"
            size="lg"
            variant="gold"
            className="mt-5 w-full justify-center"
            onClick={() => setDrawerOpen(false)}
          >
            Sign Up
          </Button>
        </div>
      </div>
    </header>
  );
}

function BurgerIcon({ open }: { open: boolean }) {
  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {open ? <path d="M18 6 6 18M6 6l12 12" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
    </svg>
  );
}
