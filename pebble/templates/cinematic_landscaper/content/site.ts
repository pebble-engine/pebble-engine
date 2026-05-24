export const SITE_TITLE       = "[Your Landscape Co.]";
export const SITE_DESCRIPTION = "Full-service landscape design and maintenance. Weekly mowing routes, seasonal installs, water-wise plant selection.";
export const TAGLINE          = "Yards. Done right.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "BOOKING SPRING INSTALLS";
export const HERO_HEADLINE          = "Yards. Done right.";
export const HERO_SUBLINE           = "Full-service landscape design + maintenance. Weekly mowing routes, seasonal installs, water-wise plant selection for your zone.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our work";
export const HERO_CTA_SECONDARY_HREF = "/services";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Weekly Maintenance",  description: "Mowing, edging, blowing, and seasonal adjustments. Same crew every visit — they get to know your yard.", icon: "Leaf"     },
  { id: "svc-2", title: "Landscape Design",    description: "Custom plant selection, bed design, and installation. Water-wise choices for your zone, installed to last.", icon: "Sprout"   },
  { id: "svc-3", title: "Seasonal Cleanups",   description: "Spring prep and fall shutdown. Mulch, pruning, gutter cleaning, and leaf removal included.",               icon: "TreePine" },
  { id: "svc-4", title: "Irrigation & Drainage", description: "Sprinkler install + repair, French-drain installation, water-wise upgrades that pay for themselves in the first summer.", icon: "Droplets" },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local landscapers. Same crew every week.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED",     sub: "[State landscape license #]" },
  { label: "INSURED",      sub: "Up to $[amount]"             },
  { label: "5-STAR RATED", sub: "[N]+ Google reviews"         },
  { label: "FAMILY-OWNED", sub: "Serving [city] since [year]" },
  { label: "WATER-WISE",   sub: "Certified [your local water authority]" },
];

export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[Maria T.], [City]";

export const CONTACT_HEADLINE = "Ready to get started?";
export const CONTACT_BODY     = "Tell us what you need. We respond within an hour during business hours.";
export const CONTACT_HOURS    = "[Mon–Fri 7am–6pm · Sat 8am–2pm]";

export const CTA_BAND_HEADLINE = "Spring installs booking now.";
export const CTA_BAND_BODY     = "Installation slots fill fast every spring. Schedule your walkthrough today.";
export const CTA_BAND_LABEL    = "Schedule a walkthrough";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Local landscape design + maintenance.";

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
  { q: "Do you handle HOA approvals?",        a: "[Yes — we've worked with [N]+ HOAs in [city]. We submit the architectural review packet so you don't have to.]" },
  { q: "What's your weekly route schedule?",  a: "[We assign you a fixed day and approximate time window. Same crew every visit. We text 30 minutes before arrival.]" },
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
