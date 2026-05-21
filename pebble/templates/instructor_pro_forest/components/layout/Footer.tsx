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
  SOCIAL,
} from "@/content/site";

/**
 * Four-column footer per training_authority DNA: brand + quick links +
 * contact + social. Outfit headings with wide letter-spacing.
 */
export function Footer() {
  const socialEntries = Object.entries(SOCIAL).filter(([_, v]) => v && !v.startsWith("["));

  return (
    <footer className="relative border-t border-border bg-card/40 mt-24">
      <div className="mx-auto max-w-6xl px-6 py-14 sm:py-20">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-2.5">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-accent/50 bg-accent/15">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-accent" aria-hidden="true">
                  <path d="M20 6 9 17l-5-5" />
                </svg>
              </span>
              <span className="font-display text-lg font-extrabold uppercase tracking-wide-12 text-fg">
                {SITE_TITLE}
              </span>
            </div>
            <p className="text-sm text-muted">{FOOTER_TAGLINE}</p>
          </div>

          {/* Pages */}
          <div>
            <h4 className="font-display text-xs font-bold uppercase tracking-wide-15 text-subtle mb-4">
              Pages
            </h4>
            <ul className="space-y-2.5">
              {FOOTER_NAV.map((link) => (
                <li key={link.href}>
                  <Link href={link.href} className="text-sm text-fg/80 hover:text-accent transition-colors">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-display text-xs font-bold uppercase tracking-wide-15 text-subtle mb-4">
              Contact
            </h4>
            <ul className="space-y-2.5 text-sm">
              <li>
                <a
                  href={`tel:${PHONE.replace(/[^+\d]/g, "")}`}
                  className="text-fg/80 hover:text-accent transition-colors"
                >
                  {PHONE_DISPLAY}
                </a>
              </li>
              <li>
                <a
                  href={`mailto:${EMAIL}`}
                  className="text-fg/80 hover:text-accent transition-colors break-all"
                >
                  {EMAIL}
                </a>
              </li>
              <li className="text-muted">{ADDRESS}</li>
              <li className="text-muted">{HOURS}</li>
            </ul>
          </div>

          {/* Service Areas / Social */}
          <div>
            <h4 className="font-display text-xs font-bold uppercase tracking-wide-15 text-subtle mb-4">
              Service Areas
            </h4>
            <ul className="space-y-2.5 text-sm">
              {SERVICE_AREAS.map((area) => (
                <li key={area} className="text-muted">
                  {area}
                </li>
              ))}
            </ul>

            {socialEntries.length > 0 && (
              <div className="mt-5 flex items-center gap-2">
                {socialEntries.map(([name, href]) => (
                  <a
                    key={name}
                    href={href}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={name}
                    className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-border bg-card/60 text-fg/80 transition-colors hover:border-accent/60 hover:text-accent"
                  >
                    <SocialIcon name={name} />
                  </a>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="mt-10 flex flex-col items-start justify-between gap-3 border-t border-border pt-6 sm:flex-row sm:items-center">
          <p className="text-xs text-ghost">
            (c) {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
          </p>
          <p className="text-xs text-ghost">
            <Link href="/contact" className="hover:text-accent transition-colors">
              Terms &amp; Liability Waiver
            </Link>
          </p>
        </div>
      </div>
    </footer>
  );
}

function SocialIcon({ name }: { name: string }) {
  const common = {
    width: 14,
    height: 14,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 2,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };
  if (name === "instagram") {
    return (
      <svg {...common}>
        <rect x="2" y="2" width="20" height="20" rx="5" />
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37zM17.5 6.5h.01" />
      </svg>
    );
  }
  if (name === "facebook") {
    return (
      <svg {...common}>
        <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z" />
      </svg>
    );
  }
  if (name === "youtube") {
    return (
      <svg {...common}>
        <path d="M22.54 6.42A2.78 2.78 0 0 0 20.6 4.5C18.88 4 12 4 12 4s-6.88 0-8.6.5A2.78 2.78 0 0 0 1.46 6.42 29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.5 8.6.5 8.6.5s6.88 0 8.6-.5a2.78 2.78 0 0 0 1.94-1.92 29 29 0 0 0 .46-5.33 29 29 0 0 0-.46-5.33z" />
        <path d="m9.75 15.02 5.75-3.27-5.75-3.27v6.54z" />
      </svg>
    );
  }
  return null;
}
