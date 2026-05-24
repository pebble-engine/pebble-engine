export const SITE_TITLE       = "[Your Plumbing Co.]";
export const SITE_DESCRIPTION = "Licensed local plumbers, family-owned. Same-day repairs, clear pricing in writing before we start.";
export const TAGLINE          = "Pipes fixed. Right. Today.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "AVAILABLE TODAY";
export const HERO_HEADLINE          = "Pipes fixed. Right. Today.";
export const HERO_SUBLINE           = "Licensed local plumbers, family-owned. We quote in writing before we start, and only fix what you approve. Most repairs done same day.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our work";
export const HERO_CTA_SECONDARY_HREF = "/services";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Leak Repair",          description: "Dripping faucets, running toilets, hidden slab leaks — we find it and fix it in one trip.", icon: "Droplets" },
  { id: "svc-2", title: "Drain & Sewer",         description: "Slow drains, clogged sewer lines, hydro-jetting. We clear it fast and show you why it happened.", icon: "Waves"    },
  { id: "svc-3", title: "Water Heater Service",  description: "Tank and tankless installation, flushing, and repair. Most water heater jobs done same day.",   icon: "Flame"    },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Licensed plumbers, family-owned.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State plumbing license #]"  },
  { label: "INSURED",      sub: "Up to $[amount]"             },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"         },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[Sarah K.], [City]";

export const CONTACT_HEADLINE = "Ready to get started?";
export const CONTACT_BODY     = "Tell us what you need. We respond within an hour during business hours.";
export const CONTACT_HOURS    = "[Mon–Fri 7am–6pm · Sat 8am–2pm]";

export const CTA_BAND_HEADLINE = "Pipe burst? Drain backed up?";
export const CTA_BAND_BODY     = "We're available today. Call us now and we'll get a tech to you fast.";
export const CTA_BAND_LABEL    = "Call us now";
export const CTA_BAND_HREF     = "tel:5555550100";

export const FOOTER_TAGLINE = "Licensed plumbing pros, available today.";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Real jobs, real customers. Tap any photo to see the details.";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Job 1 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/02.jpg", alt: "[Job 2 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/03.jpg", alt: "[Job 3 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/04.jpg", alt: "[Job 4 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/05.jpg", alt: "[Job 5 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/06.jpg", alt: "[Job 6 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/07.jpg", alt: "[Job 7 description]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/08.jpg", alt: "[Job 8 description]",  caption: "[Optional 1-line caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How it works.";
export const PROCESS_SUBLINE  = "From your first call to job-done, here's exactly what to expect — no mystery, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Tell us what you need",  description: "Call, text, or fill out the form. We respond within an hour during business hours. Free, no commitment." },
  { number: "02", title: "We come look + quote",   description: "On-site assessment with you, then a written quote in your inbox same day. Pricing is fixed before work starts." },
  { number: "03", title: "We do the work",         description: "Scheduled at your convenience. We arrive when we say we will, with the parts and tools to get it done in one trip." },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "Do you charge for estimates?",       a: "[No — every estimate is free, in writing, with no obligation. We come look, you decide.]" },
  { q: "Are you licensed and insured?",      a: "[Yes — fully licensed (#[license number]) and insured up to $[amount] for your protection.]" },
  { q: "How fast can you come out?",         a: "[Same-day in most cases for emergencies. Standard appointments usually 1-3 business days out.]" },
  { q: "What forms of payment do you take?", a: "[Cash, check, all major cards, and we offer financing on jobs over $[amount].]" },
  { q: "Do you offer a guarantee?",          a: "[Yes — [N]-year workmanship guarantee on all installations, [N] days on repairs.]" },
  { q: "What areas do you serve?",           a: "[See our service area page for the full list of cities. Generally [region] within [N] miles of [city].]" },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE = "Where we work.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned, and proud of it. If your town isn't listed, give us a call — we may still be able to help.";
export const SERVICE_AREA_MAP_EMBED = "";   // Customer adds Google Maps embed URL
export const SERVICE_AREA_CITIES: string[] = [];
export const NAV_LINKS = [
  { label: "Services",     href: "/services"     },
  { label: "Gallery",      href: "/gallery"      },
  { label: "Process",      href: "/process"      },
  { label: "Service Area", href: "/service-area" },
  { label: "FAQ",          href: "/faq"          },
  { label: "About",        href: "/about"        },
  { label: "Contact",      href: "/contact"      },
];
