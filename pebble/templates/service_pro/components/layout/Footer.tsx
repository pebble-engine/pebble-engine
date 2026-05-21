import Link from "next/link";
import {
  SITE_TITLE,
  FOOTER_TAGLINE,
  FOOTER_NAV,
  PHONE,
  PHONE_DISPLAY,
  EMAIL,
  ADDRESS,
  HOURS,
  SERVICE_AREAS,
} from "@/content/site";

export function Footer() {
  return (
    <footer className="relative border-t border-border bg-card/40 mt-24">
      <div className="mx-auto max-w-6xl px-6 py-12 sm:py-16">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-primary/20">
                <span className="h-2 w-2 rounded-full bg-primary" />
              </span>
              <span className="font-display text-lg font-semibold tracking-tight">
                {SITE_TITLE}
              </span>
            </div>
            <p className="text-sm text-muted">{FOOTER_TAGLINE}</p>
          </div>

          {/* Nav */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-subtle mb-3">
              Pages
            </h4>
            <ul className="space-y-2">
              {FOOTER_NAV.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-fg/80 hover:text-primary transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-subtle mb-3">
              Contact
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href={`tel:${PHONE.replace(/[^+\d]/g, "")}`}
                  className="text-fg/80 hover:text-primary transition-colors"
                >
                  {PHONE_DISPLAY}
                </a>
              </li>
              <li>
                <a
                  href={`mailto:${EMAIL}`}
                  className="text-fg/80 hover:text-primary transition-colors break-all"
                >
                  {EMAIL}
                </a>
              </li>
              <li className="text-muted">{ADDRESS}</li>
              <li className="text-muted">{HOURS}</li>
            </ul>
          </div>

          {/* Service areas */}
          <div>
            <h4 className="text-xs font-semibold uppercase tracking-widest text-subtle mb-3">
              Service Areas
            </h4>
            <ul className="space-y-2 text-sm">
              {SERVICE_AREAS.map((area) => (
                <li key={area} className="text-muted">
                  {area}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-3 border-t border-border pt-6 sm:flex-row sm:items-center">
          <p className="text-xs text-ghost">
            (c) {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
          </p>
          <p className="text-xs text-ghost">Licensed & insured.</p>
        </div>
      </div>
    </footer>
  );
}
