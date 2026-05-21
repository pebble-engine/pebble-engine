import * as React from "react";
import Link from "next/link";
import { ScratchyDivider } from "@/components/ui/ScratchyDivider";
import {
  SITE_TITLE,
  TAGLINE,
  WORDMARK_MAIN,
  WORDMARK_SECOND,
  WORDMARK_EYEBROW,
  FOOTER_QUICK_LINKS,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS,
  SOCIAL,
} from "@/content/site";

/**
 * Footer — four-column dark layout per DNA spec. Brand wordmark + tagline,
 * quick links, contact, studio hours. Scratchy gold divider above the
 * bottom strip.
 */
export function Footer() {
  return (
    <footer className="relative z-[2] bg-ink-secondary border-t border-ink-border">
      <div className="page-container py-section-mobile md:py-section-desktop">
        <div className="grid grid-cols-2 md:grid-cols-12 gap-10 md:gap-12">
          {/* Brand block */}
          <div className="col-span-2 md:col-span-4 flex flex-col gap-4">
            <Link
              href="/"
              className="flex flex-col items-start leading-none"
              aria-label="Home"
            >
              <span className="text-eyebrow mb-3">{WORDMARK_EYEBROW}</span>
              <span className="font-display text-3xl md:text-4xl text-ink-fg leading-none">
                {WORDMARK_MAIN}{" "}
                <span className="text-ink-primary">{WORDMARK_SECOND}</span>
              </span>
            </Link>
            <p className="text-body-lg max-w-sm mt-2">{TAGLINE}</p>
            <div className="flex items-center gap-4 mt-3">
              <a
                href={`https://instagram.com/${SOCIAL.instagram}`}
                aria-label="Instagram"
                className="text-ink-text-secondary hover:text-ink-primary transition-colors text-xs uppercase tracking-[0.22em]"
              >
                Instagram
              </a>
              <a
                href={`https://tiktok.com/@${SOCIAL.tiktok}`}
                aria-label="TikTok"
                className="text-ink-text-secondary hover:text-ink-primary transition-colors text-xs uppercase tracking-[0.22em]"
              >
                TikTok
              </a>
            </div>
          </div>

          {/* Quick links */}
          <div className="md:col-span-3">
            <h4 className="text-label mb-5">Studio</h4>
            <ul className="space-y-3">
              {FOOTER_QUICK_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="text-sm text-ink-fg hover:text-ink-primary transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div className="md:col-span-3">
            <h4 className="text-label mb-5">Contact</h4>
            <address className="not-italic text-sm text-ink-text-secondary leading-relaxed space-y-2">
              <a
                href={`mailto:${EMAIL}`}
                className="block hover:text-ink-primary transition-colors"
              >
                {EMAIL}
              </a>
              <a
                href={`tel:${PHONE}`}
                className="block hover:text-ink-primary transition-colors"
              >
                {PHONE}
              </a>
            </address>
          </div>

          {/* Visit / hours */}
          <div className="col-span-2 md:col-span-2">
            <h4 className="text-label mb-5">Visit</h4>
            <address className="not-italic text-sm text-ink-text-secondary leading-relaxed">
              <div>{ADDRESS_LINE_1}</div>
              <div>{ADDRESS_LINE_2}</div>
              <div className="mt-3 text-ink-fg">{HOURS}</div>
            </address>
          </div>
        </div>
      </div>

      {/* Scratchy divider above bottom strip */}
      <ScratchyDivider />

      <div className="page-container py-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <p className="text-xs uppercase tracking-[0.22em] text-ink-muted">
          &copy; {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
        </p>
        <p className="text-xs uppercase tracking-[0.22em] text-ink-muted">
          Brooklyn, NY.
        </p>
      </div>
    </footer>
  );
}
