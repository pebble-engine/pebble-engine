export const SITE_TITLE       = "Cinematic Services";
export const SITE_DESCRIPTION = "Trusted local pros, available today. Clear pricing, no surprises.";
export const TAGLINE          = "Available today. Real pros.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "AVAILABLE TODAY";
export const HERO_HEADLINE          = "Work that gets done right.";
export const HERO_SUBLINE           = "Family-owned local pros, available today, clear pricing in writing before we start. No surprises.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our work";
export const HERO_CTA_SECONDARY_HREF = "/services";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "[SERVICE ONE]",   description: "[1-2 sentence description of your most popular offering.]", icon: "Wrench" },
  { id: "svc-2", title: "[SERVICE TWO]",   description: "[1-2 sentence description of your second core offering.]",  icon: "Hammer" },
  { id: "svc-3", title: "[SERVICE THREE]", description: "[1-2 sentence description of your third core offering.]",   icon: "Truck"  },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local pros you can trust.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State + license #]"      },
  { label: "INSURED",      sub: "Up to $[amount]"          },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"      },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[First Name L.], [City]";

export const CONTACT_HEADLINE = "Ready to get started?";
export const CONTACT_BODY     = "Tell us what you need. We respond within an hour during business hours.";
export const CONTACT_HOURS    = "[Mon–Fri 7am–6pm · Sat 8am–2pm]";

export const CTA_BAND_HEADLINE = "Available today.";
export const CTA_BAND_BODY     = "Most jobs quoted within 24 hours. Same-week service in most cases.";
export const CTA_BAND_LABEL    = "Get a free quote";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Trusted local pros, available today.";
export const NAV_LINKS = [
  { label: "Services", href: "/services" },
  { label: "About",    href: "/about"    },
  { label: "Contact",  href: "/contact"  },
];
