import * as React from "react";
import Link from "next/link";
import {
  SITE_TITLE,
  WORDMARK_MARK,
  WORDMARK_MAIN,
  FOOTER_LEGAL_LINKS,
} from "@/content/site";

/**
 * Footer — three-part horizontal band on the surface color.
 * Left: logo mark + wordmark. Center: terms/privacy/accessibility/fair-housing
 * legal links. Right: copyright line.
 */
export function Footer() {
  return (
    <footer className="bg-surface border-t border-border">
      <div className="page-container py-12">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-8">
          {/* Left — logo */}
          <Link
            href="/"
            className="flex items-center gap-3 leading-none"
            aria-label="Home"
          >
            <span
              aria-hidden="true"
              className="inline-flex h-7 w-7 items-center justify-center bg-accent font-display font-black text-xs text-fg"
            >
              {WORDMARK_MARK}
            </span>
            <span className="font-display font-black text-base uppercase tracking-tighter text-fg">
              {WORDMARK_MAIN}
            </span>
          </Link>

          {/* Center — legal links */}
          <nav aria-label="Legal" className="flex flex-wrap items-center gap-x-8 gap-y-3">
            {FOOTER_LEGAL_LINKS.map((l) => (
              <Link
                key={l.label}
                href={l.href}
                className="text-eyebrow hover:text-accent transition-colors"
              >
                {l.label}
              </Link>
            ))}
          </nav>

          {/* Right — copyright */}
          <p className="text-eyebrow">
            &copy; {new Date().getFullYear()} {SITE_TITLE}
          </p>
        </div>
      </div>
    </footer>
  );
}
