import * as React from "react";
import Link from "next/link";
import {
  SITE_TITLE,
  TAGLINE,
  WORDMARK_EYEBROW,
  WORDMARK_MAIN,
  FOOTER_SHOP_LINKS,
  FOOTER_HOUSE_LINKS,
  FOOTER_HELP_LINKS,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS,
  SOCIAL,
} from "@/content/site";

/**
 * Footer — editorial multi-column footer with cursive eyebrow.
 */
export function Footer() {
  return (
    <footer className="bg-surface-container border-t border-outline-variant/40">
      <div className="page-container py-section-mobile md:py-24">
        <div className="grid grid-cols-2 md:grid-cols-12 gap-10 md:gap-12">
          {/* Brand block */}
          <div className="col-span-2 md:col-span-4 flex flex-col gap-4">
            <Link href="/" className="flex flex-col items-start leading-none" aria-label="Home">
              <span className="font-script text-2xl text-tertiary -mb-2">
                {WORDMARK_EYEBROW}
              </span>
              <span className="font-display text-2xl tracking-[0.16em] uppercase text-on-surface">
                {WORDMARK_MAIN}
              </span>
            </Link>
            <p className="text-body-lg max-w-sm">{TAGLINE}</p>
            <div className="flex items-center gap-4 mt-2">
              <a
                href={`https://instagram.com/${SOCIAL.instagram}`}
                aria-label="Instagram"
                className="text-on-surface-variant hover:text-primary transition-colors text-xs uppercase tracking-[0.18em]"
              >
                Instagram
              </a>
              <a
                href={`https://tiktok.com/@${SOCIAL.tiktok}`}
                aria-label="TikTok"
                className="text-on-surface-variant hover:text-primary transition-colors text-xs uppercase tracking-[0.18em]"
              >
                TikTok
              </a>
              <a
                href={`https://pinterest.com/${SOCIAL.pinterest}`}
                aria-label="Pinterest"
                className="text-on-surface-variant hover:text-primary transition-colors text-xs uppercase tracking-[0.18em]"
              >
                Pinterest
              </a>
            </div>
          </div>

          {/* Shop */}
          <div className="md:col-span-2">
            <h4 className="text-label mb-4">Shop</h4>
            <ul className="space-y-3">
              {FOOTER_SHOP_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="text-sm text-on-surface hover:text-primary transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* House */}
          <div className="md:col-span-2">
            <h4 className="text-label mb-4">House</h4>
            <ul className="space-y-3">
              {FOOTER_HOUSE_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="text-sm text-on-surface hover:text-primary transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Help */}
          <div className="md:col-span-2">
            <h4 className="text-label mb-4">Help</h4>
            <ul className="space-y-3">
              {FOOTER_HELP_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="text-sm text-on-surface hover:text-primary transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Visit */}
          <div className="col-span-2 md:col-span-2">
            <h4 className="text-label mb-4">Visit</h4>
            <address className="not-italic text-sm text-on-surface-variant leading-relaxed">
              <div>{ADDRESS_LINE_1}</div>
              <div>{ADDRESS_LINE_2}</div>
              <div className="mt-3">{HOURS}</div>
              <div className="mt-3">
                <a href={`mailto:${EMAIL}`} className="hover:text-primary transition-colors">
                  {EMAIL}
                </a>
              </div>
              <div>
                <a href={`tel:${PHONE}`} className="hover:text-primary transition-colors">
                  {PHONE}
                </a>
              </div>
            </address>
          </div>
        </div>

        {/* Footer bottom strip */}
        <div className="mt-16 pt-8 border-t border-outline-variant/40 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.18em] text-on-surface-variant">
            &copy; {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
          </p>
          <p className="text-xs uppercase tracking-[0.18em] text-on-surface-variant">
            Made in SoHo, NY.
          </p>
        </div>
      </div>
    </footer>
  );
}
