import * as React from "react";
import Link from "next/link";
import {
  SITE_TITLE,
  TAGLINE,
  FOOTER_VISIT_LINKS,
  FOOTER_HOUSE_LINKS,
  ADDRESS_LINE_1,
  ADDRESS_LINE_2,
  EMAIL,
  PHONE,
  HOURS_LINES,
  SOCIAL,
} from "@/content/site";

/**
 * Footer — three-column minimal. Brand + Visit Us + Contact, with a
 * thin top border and a copyright line at the very bottom.
 */
export function Footer() {
  return (
    <footer className="bg-cream-alt border-t border-edge/60">
      <div className="page-container py-section-mobile md:py-24">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10 md:gap-12">
          {/* Brand block */}
          <div className="md:col-span-5 flex flex-col gap-4">
            <Link
              href="/"
              className="font-display text-2xl text-ink leading-none"
              aria-label={`${SITE_TITLE} — home`}
            >
              {SITE_TITLE}
            </Link>
            <p className="text-body-lg max-w-sm">{TAGLINE}</p>
            <a
              href={`https://instagram.com/${SOCIAL.instagram}`}
              aria-label="Instagram"
              className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-ink-soft hover:text-crust transition-colors"
            >
              Instagram
            </a>
          </div>

          {/* Visit Us */}
          <div className="md:col-span-3">
            <h4 className="text-label mb-4">Visit us</h4>
            <address className="not-italic text-sm text-ink-soft leading-relaxed mb-4">
              <div>{ADDRESS_LINE_1}</div>
              <div>{ADDRESS_LINE_2}</div>
            </address>
            <ul className="space-y-2">
              {HOURS_LINES.map((row) => (
                <li
                  key={row.label}
                  className="flex justify-between text-sm text-ink-soft gap-4"
                >
                  <span className="font-medium text-ink">{row.label}</span>
                  <span>{row.value}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div className="md:col-span-2">
            <h4 className="text-label mb-4">Contact</h4>
            <ul className="space-y-3 text-sm">
              <li>
                <a
                  href={`mailto:${EMAIL}`}
                  className="text-ink-soft hover:text-crust transition-colors"
                >
                  {EMAIL}
                </a>
              </li>
              <li>
                <a
                  href={`tel:${PHONE}`}
                  className="text-ink-soft hover:text-crust transition-colors"
                >
                  {PHONE}
                </a>
              </li>
            </ul>
          </div>

          {/* House links */}
          <div className="md:col-span-2">
            <h4 className="text-label mb-4">More</h4>
            <ul className="space-y-3">
              {FOOTER_HOUSE_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="text-sm text-ink-soft hover:text-crust transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
              {FOOTER_VISIT_LINKS.map((l) => (
                <li key={l.href + l.label}>
                  <Link
                    href={l.href}
                    className="text-sm text-ink-soft hover:text-crust transition-colors"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom strip */}
        <div className="mt-16 pt-8 border-t border-edge/60 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
          <p className="text-xs uppercase tracking-[0.18em] text-ink-soft">
            &copy; {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
          </p>
          <p className="text-xs uppercase tracking-[0.18em] text-ink-soft">
            Made in Brooklyn.
          </p>
        </div>
      </div>
    </footer>
  );
}
