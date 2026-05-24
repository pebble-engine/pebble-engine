"use client";
import Link from "next/link";
import { FadeIn } from "@/components/ui/FadeIn";

export function Navbar() {
  return (
    <header className="fixed top-0 inset-x-0 z-50">
      <FadeIn delay={0} duration={0.9} className="px-6 md:px-12 lg:px-16 py-4 flex items-center justify-between"
        style={{ background: "var(--color-bg)", borderBottom: "1px solid var(--color-border)" }}
      >
        <Link href="/" className="text-xl font-medium tracking-tight" style={{ color: "var(--color-text-primary)" }}>
          Indie Bookstore
        </Link>

        <nav className="hidden md:flex gap-8 text-sm" style={{ color: "var(--color-text-secondary)" }}>
          <Link href="/services" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">Services</Link>
          <Link href="/faq" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">FAQ</Link>
          <Link href="/about" className="hover:text-[var(--color-text-primary)] transition-colors font-medium">About</Link>
        </nav>

        <a href="tel:[BUSINESS PHONE]" className="bg-[var(--color-surface-2)] text-[var(--color-text-primary)] px-5 py-2 rounded-lg text-sm font-medium hover:opacity-80 transition-opacity focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-transparent min-h-[44px]" data-pebble-id="pb-ebb781">
          Call Us
        </a>
      </FadeIn>
    </header>
  );
}