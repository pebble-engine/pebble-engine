import { SITE_TITLE, FOOTER_TAGLINE, NAV_LINKS, PHONE, EMAIL, ADDRESS } from "@/content/site";

export function Footer() {
  return (
    <footer className="bg-[var(--color-surface-2)] border-t border-[var(--color-border)]">
      <div className="max-w-6xl mx-auto px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {/* Col 1: brand */}
          <div>
            <p className="font-[family-name:var(--font-display)] text-[18px] uppercase text-[var(--color-text-primary)] tracking-tight">
              {SITE_TITLE}
            </p>
            <p className="mt-2 text-[14px] text-[var(--color-text-secondary)] leading-relaxed">
              {FOOTER_TAGLINE}
            </p>
          </div>

          {/* Col 2: nav */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-4">
              Navigation
            </p>
            <ul className="space-y-3">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-[14px] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Col 3: contact */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-widest text-[var(--color-text-secondary)] mb-4">
              Contact
            </p>
            <ul className="space-y-3">
              <li className="text-[14px] text-[var(--color-text-secondary)]">{PHONE}</li>
              <li className="text-[14px] text-[var(--color-text-secondary)]">{EMAIL}</li>
              <li className="text-[14px] text-[var(--color-text-secondary)]">{ADDRESS}</li>
            </ul>
          </div>
        </div>

        <p className="mt-12 text-[12px] text-[var(--color-text-secondary)] text-center">
          © {new Date().getFullYear()} {SITE_TITLE}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
