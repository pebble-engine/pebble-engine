"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { cn } from "@/lib/cn";
import { ThemeToggle } from "@/components/ui/ThemeToggle";
import { Button } from "@/components/ui/Button";
import { CallChip } from "@/components/ui/CallChip";
import { NAV_LINKS, SITE_TITLE } from "@/content/site";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Toggle blur intensity when the user scrolls past the hero edge.
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // Lock body scroll when the mobile drawer is open.
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
            ? "border-border bg-card/70 backdrop-blur-xl shadow-lg shadow-black/10"
            : "border-transparent bg-card/30 backdrop-blur-md",
        )}
      >
        {/* Logo / wordmark */}
        <Link href="/" className="flex items-center gap-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full">
          <span className="relative inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary/20">
            <span className="absolute inset-0 rounded-full ring-1 ring-primary/50 animate-glow-pulse" />
            <span className="h-2 w-2 rounded-full bg-primary" />
          </span>
          <span className="font-display text-base font-semibold tracking-tight text-fg">
            {SITE_TITLE}
          </span>
        </Link>

        {/* Desktop links */}
        <ul className="hidden items-center gap-7 md:flex">
          {NAV_LINKS.map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className="text-sm text-fg/80 hover:text-primary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full px-1"
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right cluster */}
        <div className="flex items-center gap-2 sm:gap-3">
          <ThemeToggle className="hidden sm:inline-flex" />
          <Button href="/contact" size="md" shimmer className="hidden sm:inline-flex">
            Book Now
          </Button>
          <button
            type="button"
            aria-label="Open menu"
            aria-expanded={drawerOpen}
            onClick={() => setDrawerOpen((v) => !v)}
            className="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card/40 text-fg/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
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
        <div className="absolute inset-0 bg-bg/85 backdrop-blur-xl" />
        <div
          className={cn(
            "absolute inset-x-0 top-20 mx-4 rounded-3xl border border-border bg-card/90 p-6 transition-transform duration-300",
            drawerOpen ? "translate-y-0" : "-translate-y-4",
          )}
          onClick={(e) => e.stopPropagation()}
        >
          <ul className="flex flex-col gap-1">
            {NAV_LINKS.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="block rounded-2xl px-4 py-3 text-base font-medium text-fg hover:bg-primary/10"
                  onClick={() => setDrawerOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
          <div className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-4">
            <ThemeToggle />
            <CallChip />
          </div>
          <Button href="/contact" size="lg" shimmer className="mt-4 w-full justify-center" onClick={() => setDrawerOpen(false)}>
            Book Now
          </Button>
        </div>
      </div>
    </header>
  );
}

function BurgerIcon({ open }: { open: boolean }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {open ? <path d="M18 6 6 18M6 6l12 12" /> : <path d="M3 6h18M3 12h18M3 18h18" />}
    </svg>
  );
}
