"use client";

/**
 * LandingNav — Phase 40j (2026-05-21).
 *
 * Replaces the inline `TopNavBar()` that used to live inside
 * welcome-phase.tsx. Pattern adapted from a 21st.dev "header-2" Marc
 * liked: sticky pill that shrinks + adds backdrop blur + shadow once
 * the user scrolls past the threshold, with a full-screen mobile menu
 * for ≤md viewports.
 *
 * What's preserved from the old TopNavBar:
 *   - Pebble brand mark on the left, anchored to the page top
 *   - The four section-anchor links (How it works / Looks / Pricing / Start)
 *   - Smooth-scroll behavior on link click
 *   - Light-mode color palette (the landing forces light tokens)
 *
 * What's new:
 *   - Sign In (link → /login) + Get Started (primary, link → /signup)
 *     CTAs on the right, matching every other modern SaaS landing
 *   - Sticky behavior with a scroll threshold (shrinks pill at >10px)
 *   - Mobile menu toggle (hamburger / X via lucide-react)
 *   - All-section overflow scroll-lock when the mobile menu is open
 */

import React from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";
import { cn } from "@/lib/utils";

/** Anchor links shown in the nav. Hashes match the section IDs in
    welcome-phase.tsx (#how, #looks, #pricing, #start). */
const LINKS = [
  { label: "How it works", href: "#how"     },
  { label: "Looks",        href: "#looks"   },
  { label: "Pricing",      href: "#pricing" },
  { label: "Start",        href: "#start"   },
];

/** Scroll listener hook — same pattern as the 21st.dev `use-scroll`,
    inlined so we don't need a separate file. Returns true once the
    window scrollY exceeds the threshold. */
function useScrolled(threshold: number): boolean {
  const [scrolled, setScrolled] = React.useState(false);
  React.useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);
  return scrolled;
}

/** Smooth-scroll anchor click. Preserves the old TopNavBar's behavior. */
function handleAnchorClick(e: React.MouseEvent<HTMLAnchorElement>, href: string) {
  if (!href.startsWith("#")) return;
  e.preventDefault();
  const id = href.replace("#", "");
  if (!id) {
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
}

/** Pebble brand mark for the nav. Phase 40k (2026-05-21) — Marc's call:
    nav uses ONE professional font end-to-end. Switched from Cinzel
    (the global `font-logo`) to Plus Jakarta Sans (the body sans) so
    brand + links + buttons all share the same typeface family. Heavy
    weight + tight tracking gives the wordmark feel without needing a
    separate serif. The cycling multilingual `RotatingPebbleLogo` stays
    in the footer where Cinzel still has room to breathe. */
function PebbleMark({ className = "" }: { className?: string }) {
  return (
    <Link
      href="/"
      onClick={(e) => handleAnchorClick(e, "#")}
      className={cn(
        "inline-flex items-center text-[22px] font-extrabold tracking-tight text-foreground",
        "hover:text-foreground/85 transition-colors",
        className,
      )}
      aria-label="Pebble — home"
    >
      Pebble<span aria-hidden className="text-[#3054ff]">.</span>
    </Link>
  );
}

export function LandingNav() {
  const [open, setOpen] = React.useState(false);
  const scrolled = useScrolled(10);

  // Lock body scroll while the mobile menu is open so the page behind
  // doesn't scroll with finger drags.
  React.useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  // Close the mobile menu when a link is clicked.
  const handleMobileLink = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    handleAnchorClick(e, href);
    setOpen(false);
  };

  return (
    <header
      // Phase 40k — explicit Plus Jakarta Sans on the whole header so
      // brand, links, and buttons share one professional typeface
      // (matches Marc's "Efferd" reference screenshot).
      style={{ fontFamily: "var(--font-plus-jakarta-sans), system-ui, sans-serif" }}
      className={cn(
        "sticky top-0 z-50 mx-auto w-full max-w-5xl border-b border-transparent",
        "md:rounded-full md:border md:transition-all md:ease-out",
        // scrolled + closed → shrunk pill with backdrop, sits 16px from top
        scrolled && !open && [
          "bg-card/95 supports-[backdrop-filter]:bg-card/65 backdrop-blur-xl",
          "border-border md:top-4 md:max-w-4xl",
          "shadow-[0_8px_32px_rgba(31,29,26,0.08)]",
        ],
        // open mobile menu → solid surface so menu reads cleanly
        open && "bg-card/95",
      )}
    >
      <nav
        className={cn(
          "flex h-14 w-full items-center justify-between gap-3 px-4",
          "md:h-12 md:transition-all md:ease-out",
          scrolled && "md:px-3",
        )}
        aria-label="Primary"
      >
        {/* Brand left */}
        <PebbleMark />

        {/* Center anchor links (md+) */}
        <div className="hidden md:flex items-center gap-1">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={(e) => handleAnchorClick(e, link.href)}
              className={cn(
                "inline-flex items-center px-3.5 py-1.5 rounded-full text-[15px] font-semibold tracking-tight",
                "text-foreground/85 hover:text-foreground hover:bg-accent",
                "transition-colors duration-150",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              )}
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* CTAs right (md+) */}
        <div className="hidden md:flex items-center gap-2">
          <Link
            href="/login"
            className={cn(
              "inline-flex items-center justify-center rounded-full border border-border px-4 py-1.5",
              "text-[15px] font-semibold tracking-tight text-foreground bg-transparent",
              "hover:bg-accent transition-colors",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            )}
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className={cn(
              "inline-flex items-center justify-center rounded-full px-4 py-1.5",
              "text-[15px] font-semibold tracking-tight text-background bg-foreground",
              "hover:opacity-90 transition-opacity",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
            )}
          >
            Get Started
          </Link>
        </div>

        {/* Mobile toggle (≤md) */}
        <button
          type="button"
          onClick={() => setOpen((o) => !o)}
          aria-expanded={open}
          aria-label={open ? "Close menu" : "Open menu"}
          className={cn(
            "md:hidden inline-flex items-center justify-center w-10 h-10 rounded-full",
            "border border-border bg-transparent text-foreground",
            "hover:bg-accent transition-colors",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          )}
        >
          {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </nav>

      {/* Mobile full-screen menu (≤md). Anchored below the nav row, fills
          rest of viewport. Auto-closes on link click. */}
      <div
        className={cn(
          "fixed top-14 left-0 right-0 bottom-0 z-50 md:hidden",
          "bg-background/95 backdrop-blur-xl border-y border-border",
          "flex flex-col overflow-hidden",
          open ? "flex" : "hidden",
        )}
      >
        <div className="flex flex-col justify-between gap-y-4 p-6 h-full">
          <div className="grid gap-y-1">
            {LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleMobileLink(e, link.href)}
                className={cn(
                  "inline-flex items-center justify-start px-4 py-3 rounded-xl",
                  "text-xl font-semibold tracking-tight text-foreground",
                  "hover:bg-accent transition-colors",
                )}
              >
                {link.label}
              </a>
            ))}
          </div>
          <div className="flex flex-col gap-2 pb-6">
            <Link
              href="/login"
              onClick={() => setOpen(false)}
              className={cn(
                "inline-flex items-center justify-center rounded-full border border-border w-full py-3",
                "text-base font-medium text-foreground bg-transparent",
                "hover:bg-accent transition-colors",
              )}
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              onClick={() => setOpen(false)}
              className={cn(
                "inline-flex items-center justify-center rounded-full w-full py-3",
                "text-base font-semibold text-background bg-foreground",
                "hover:opacity-90 transition-opacity",
              )}
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default LandingNav;
