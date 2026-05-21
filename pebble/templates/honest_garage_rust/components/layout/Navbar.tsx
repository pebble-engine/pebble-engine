"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";
import { NAV_LINKS, SITE_TITLE } from "@/content/site";

/**
 * Industrial navbar with rust-tile brand glyph + wordmark. The brand tile sits
 * against the warm-dark page bg (per the auto_honest_diag DNA). Adds a subtle
 * bg-card backdrop after 100px of scroll.
 */
export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 100);
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

  // First two characters of the brand → square tile glyph (e.g. "RB").
  const tileGlyph = SITE_TITLE.split(" ")
    .map((w) => w[0])
    .filter(Boolean)
    .slice(0, 2)
    .join("")
    .toUpperCase() || "RB";

  return (
    <header
      className={cn(
        "fixed inset-x-0 top-1 z-50 transition-all duration-300",
        scrolled ? "bg-bg/90 backdrop-blur-md border-b border-white/5" : "bg-transparent",
      )}
    >
      <nav className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-4">
        {/* Brand tile + wordmark */}
        <Link
          href="/"
          className="flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        >
          <span
            className="inline-flex h-8 w-8 items-center justify-center bg-primary text-fg font-mono text-xs font-bold tracking-wider"
            aria-hidden="true"
          >
            {tileGlyph}
          </span>
          <span className="stencil-filled text-xl">{SITE_TITLE}</span>
        </Link>

        {/* Desktop links */}
        <ul className="hidden items-center gap-7 md:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="font-mono text-xs font-bold uppercase tracking-[0.12em] text-fg/80 hover:text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right cluster */}
        <div className="flex items-center gap-2">
          <Link href="/contact" className="btn-primary hidden sm:inline-flex">
            GET ESTIMATE
          </Link>
          <button
            type="button"
            aria-label="Open menu"
            aria-expanded={drawerOpen}
            onClick={() => setDrawerOpen((v) => !v)}
            className="md:hidden inline-flex h-10 w-10 items-center justify-center border border-white/10 bg-card/40 text-fg/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
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
        <div className="absolute inset-0 bg-bg/95 backdrop-blur-xl" />
        <div
          className={cn(
            "absolute inset-x-0 top-20 mx-4 border border-white/10 bg-card/95 p-6 transition-transform duration-300",
            drawerOpen ? "translate-y-0" : "-translate-y-4",
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="block border-l-2 border-transparent hover:border-primary px-4 py-3 font-mono text-sm font-bold uppercase tracking-[0.12em] text-fg hover:bg-primary/5"
                  onClick={() => setDrawerOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
          <Link
            href="/contact"
            className="btn-primary mt-4 w-full"
            onClick={() => setDrawerOpen(false)}
          >
            GET ESTIMATE
          </Link>
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
