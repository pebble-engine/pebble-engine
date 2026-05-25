"use client";

/**
 * LandingNav — Phase 40j (2026-05-21).
 *
 * Phase 56 updates (2026-05-22):
 *   - Full-width edge-to-edge bar (removed max-w-5xl / mx-auto constraint)
 *   - Bigger text throughout (logo 26px, links + CTAs 17px)
 *   - Blue radial gradient background matching §6 pricing section
 *   - Gradient fades out gracefully when scrolled pill activates
 */

import React from "react";
import Link from "next/link";
import { Menu, X, LayoutGrid, ChevronDown, Sparkles, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth-provider";

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

/** Pebble brand mark for the nav.
 *
 *  Unauthed (or auth still loading): plain link back to the landing top.
 *
 *  Authed: button that opens a dropdown with quick-jumps into the app
 *  (dashboard, start a build) + sign out. Marc's 2026-05-23 request —
 *  a returning logged-in user looking at the landing page should be
 *  able to launch back into product surfaces from the most prominent
 *  affordance on the page (the brand mark itself), not just from the
 *  right-side CTA. */
function PebbleMark({ className = "" }: { className?: string }) {
  const { user, loading: authLoading, signOut } = useAuth();
  const isAuthed = !authLoading && !!user;
  const [open, setOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement | null>(null);

  // Click-outside closes the menu. Same pattern as components/auth-menu.tsx.
  React.useEffect(() => {
    if (!open) return;
    function onDocClick(e: MouseEvent) {
      if (!containerRef.current?.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, [open]);

  // Esc closes the menu when it has focus.
  React.useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  const markText = (
    <>
      Pebble<span aria-hidden className="text-[#3054ff]">.</span>
    </>
  );
  const markClasses = cn(
    "inline-flex items-center text-[28px] font-extrabold tracking-tight text-foreground",
    "hover:text-foreground/85 transition-colors",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-md",
    className,
  );

  if (!isAuthed) {
    return (
      <Link
        href="/"
        onClick={(e) => handleAnchorClick(e, "#")}
        className={markClasses}
        aria-label="Pebble — home"
      >
        {markText}
      </Link>
    );
  }

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={cn(markClasses, "gap-1.5 cursor-pointer")}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={open ? "Close Pebble menu" : "Open Pebble menu"}
      >
        {markText}
        <ChevronDown
          aria-hidden
          className={cn(
            "h-4 w-4 text-muted-foreground transition-transform duration-150",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <div
          role="menu"
          className={cn(
            "absolute left-0 mt-2 w-64 z-50 overflow-hidden",
            "rounded-2xl border border-border bg-card shadow-[0_12px_40px_rgba(31,29,26,0.18)]",
          )}
        >
          {user?.email && (
            <div className="px-4 py-3 border-b border-border">
              <p className="text-[11px] uppercase tracking-widest text-muted-foreground">
                Signed in as
              </p>
              <p className="text-sm font-semibold text-foreground truncate mt-0.5">
                {user.email}
              </p>
            </div>
          )}
          <Link
            href="/dashboard"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-foreground hover:bg-accent transition-colors"
          >
            <LayoutGrid className="h-4 w-4 text-muted-foreground" />
            Open dashboard
          </Link>
          <Link
            href="/workspace"
            onClick={() => setOpen(false)}
            className="flex items-center gap-3 px-4 py-3 text-sm font-semibold text-foreground hover:bg-accent transition-colors"
          >
            <Sparkles className="h-4 w-4 text-muted-foreground" />
            Start something new
          </Link>
          <button
            type="button"
            onClick={async () => {
              setOpen(false);
              await signOut();
            }}
            className="w-full text-left flex items-center gap-3 px-4 py-3 text-sm font-semibold text-foreground hover:bg-accent transition-colors border-t border-border"
          >
            <LogOut className="h-4 w-4 text-muted-foreground" />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}

export function LandingNav() {
  const [open, setOpen] = React.useState(false);
  const scrolled = useScrolled(10);
  // Phase 58b — when the user is signed in, the nav must reflect that.
  // Previously the right-side CTAs were always "Sign In" + "Get Started",
  // so a signed-in user returning to the landing page sees them and clicks
  // Sign In thinking they're signed out → re-OAuth loop → confusion.
  const { user, loading: authLoading } = useAuth();
  const isAuthed = !authLoading && !!user;

  React.useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [open]);

  const handleMobileLink = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    handleAnchorClick(e, href);
    setOpen(false);
  };

  return (
    <header
      style={{ fontFamily: "var(--font-plus-jakarta-sans), system-ui, sans-serif" }}
      className={cn(
        // Phase 56: full-width edge-to-edge — no max-w or mx-auto in default state
        "sticky top-0 z-50 w-full border-b border-transparent",
        "transition-all duration-300 ease-out",
        // Scrolled: shrink to centered pill (same as before)
        scrolled && !open && [
          "bg-card/95 supports-[backdrop-filter]:bg-card/65 backdrop-blur-xl",
          "border-border md:mx-auto md:top-4 md:rounded-full md:max-w-4xl",
          "shadow-[0_8px_32px_rgba(31,29,26,0.08)]",
        ],
        open && "bg-card/95",
      )}
    >
      {/* Blue radial gradient — same palette as §6 pricing section.
          Fades out when scrolled so the pill state stays clean. */}
      <div
        aria-hidden
        className={cn(
          "pointer-events-none absolute inset-0 transition-opacity duration-300",
          "bg-[radial-gradient(ellipse_80%_160%_at_50%_0%,rgba(48,84,255,0.13)_0%,rgba(48,84,255,0.05)_55%,transparent_100%)]",
          scrolled || open ? "opacity-0" : "opacity-100",
        )}
      />

      <nav
        className={cn(
          "relative flex h-16 w-full items-center justify-between gap-3",
          "px-6 sm:px-10 lg:px-16",
          "transition-all ease-out",
          scrolled && "md:h-14 md:px-6",
        )}
        aria-label="Primary"
      >
        {/* Brand left */}
        <PebbleMark />

        {/* Center anchor links (md+) */}
        <div className="hidden md:flex items-center gap-0.5 flex-shrink min-w-0">
          {LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={(e) => handleAnchorClick(e, link.href)}
              className={cn(
                "inline-flex items-center whitespace-nowrap px-3 py-2 rounded-full",
                "text-[15px] font-semibold tracking-tight",
                "text-foreground/85 hover:text-foreground hover:bg-accent",
                "transition-colors duration-150",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
              )}
            >
              {link.label}
            </a>
          ))}
        </div>

        {/* CTAs right (md+) — auth-aware. Signed-in users see Dashboard
            instead of Sign In + Get Started so the nav reflects reality
            and they don't double-OAuth out of confusion. */}
        <div className="hidden md:flex items-center gap-2 flex-shrink-0">
          {isAuthed ? (
            <>
              <Link
                href="/dashboard"
                className={cn(
                  "inline-flex items-center justify-center gap-1.5 whitespace-nowrap rounded-full border border-border px-4 py-2",
                  "text-[15px] font-semibold tracking-tight text-foreground bg-transparent",
                  "hover:bg-accent transition-colors",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
                )}
              >
                <LayoutGrid className="w-4 h-4" />
                Dashboard
              </Link>
              <Link
                href="/workspace"
                className={cn(
                  "inline-flex items-center justify-center whitespace-nowrap rounded-full px-4 py-2",
                  "text-[15px] font-semibold tracking-tight text-white",
                  "bg-[linear-gradient(135deg,#3054ff,#6b8aff)]",
                  "hover:brightness-110 transition-[filter] duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
                )}
                title={user?.email ?? undefined}
              >
                Start a build
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className={cn(
                  "inline-flex items-center justify-center whitespace-nowrap rounded-full border border-border px-4 py-2",
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
                  "inline-flex items-center justify-center whitespace-nowrap rounded-full px-4 py-2",
                  "text-[15px] font-semibold tracking-tight text-white",
                  "bg-[linear-gradient(135deg,#3054ff,#6b8aff)]",
                  "hover:brightness-110 transition-[filter] duration-150",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
                )}
              >
                Get Started
              </Link>
            </>
          )}
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

      {/* Mobile full-screen menu (≤md). */}
      <div
        className={cn(
          "fixed top-16 left-0 right-0 bottom-0 z-50 md:hidden",
          "bg-background/95 backdrop-blur-xl border-y border-border",
          "flex flex-col overflow-hidden",
          "[overscroll-behavior:contain]",
          open ? "flex" : "hidden",
        )}
      >
        <div className="flex flex-col justify-between gap-y-4 p-6 h-full pb-safe">
          <div className="grid gap-y-1">
            {LINKS.map((link) => (
              <a
                key={link.href}
                href={link.href}
                onClick={(e) => handleMobileLink(e, link.href)}
                className={cn(
                  "inline-flex items-center justify-start px-4 py-3 rounded-xl",
                  "text-2xl font-semibold tracking-tight text-foreground",
                  "hover:bg-accent transition-colors",
                )}
              >
                {link.label}
              </a>
            ))}
          </div>
          <div className="flex flex-col gap-2 pb-6">
            {isAuthed ? (
              <>
                <Link
                  href="/dashboard"
                  onClick={() => setOpen(false)}
                  className={cn(
                    "inline-flex items-center justify-center gap-2 rounded-full border border-border w-full py-3",
                    "text-lg font-semibold text-foreground bg-transparent",
                    "hover:bg-accent transition-colors",
                  )}
                >
                  <LayoutGrid className="w-5 h-5" />
                  Dashboard
                </Link>
                <Link
                  href="/workspace"
                  onClick={() => setOpen(false)}
                  className={cn(
                    "inline-flex items-center justify-center rounded-full w-full py-3",
                    "text-lg font-semibold text-background bg-foreground",
                    "hover:opacity-90 transition-opacity",
                  )}
                >
                  Start a build
                </Link>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  onClick={() => setOpen(false)}
                  className={cn(
                    "inline-flex items-center justify-center rounded-full border border-border w-full py-3",
                    "text-lg font-semibold text-foreground bg-transparent",
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
                    "text-lg font-semibold text-background bg-foreground",
                    "hover:opacity-90 transition-opacity",
                  )}
                >
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

export default LandingNav;
