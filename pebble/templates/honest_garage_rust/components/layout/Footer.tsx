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
} from "@/content/site";

export function Footer() {
  return (
    <footer className="relative border-t border-white/10 bg-card/40 mt-24">
      <div className="mx-auto max-w-6xl px-6 py-12 sm:py-16">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span
                className="inline-flex h-7 w-7 items-center justify-center bg-primary text-bg font-mono text-[10px] font-bold tracking-wider"
                aria-hidden="true"
              >
                {SITE_TITLE.split(" ")
                  .map((w) => w[0])
                  .filter(Boolean)
                  .slice(0, 2)
                  .join("")
                  .toUpperCase()}
              </span>
              <span className="stencil-filled text-lg">{SITE_TITLE}</span>
            </div>
            <p className="font-mono text-xs uppercase tracking-[0.12em] text-muted">
              {FOOTER_TAGLINE}
            </p>
          </div>

          {/* Pages */}
          <div>
            <h4 className="ref-code mb-3">// PAGES</h4>
            <ul className="space-y-2">
              {FOOTER_NAV.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="font-mono text-xs uppercase tracking-[0.12em] text-fg/80 hover:text-primary transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="ref-code mb-3">// CONTACT</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href={`tel:${PHONE.replace(/[^+\d]/g, "")}`}
                  className="font-mono text-xs uppercase tracking-[0.12em] text-fg/80 hover:text-primary transition-colors"
                >
                  {PHONE_DISPLAY}
                </a>
              </li>
              <li>
                <a
                  href={`mailto:${EMAIL}`}
                  className="font-mono text-xs uppercase tracking-[0.12em] text-fg/80 hover:text-primary transition-colors break-all"
                >
                  {EMAIL}
                </a>
              </li>
              <li className="font-mono text-xs uppercase tracking-[0.12em] text-muted">
                {ADDRESS}
              </li>
            </ul>
          </div>

          {/* Hours */}
          <div>
            <h4 className="ref-code mb-3">// HOURS</h4>
            <p className="font-mono text-xs uppercase tracking-[0.12em] text-muted">
              {HOURS}
            </p>
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-3 border-t border-white/10 pt-6 sm:flex-row sm:items-center">
          <p className="ref-code">
            (c) {new Date().getFullYear()} — {SITE_TITLE.toUpperCase()}. INDEPENDENT SHOP.
          </p>
          <p className="ref-code">LICENSED & INSURED.</p>
        </div>
      </div>
    </footer>
  );
}
