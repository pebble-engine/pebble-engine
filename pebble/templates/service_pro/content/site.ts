/**
 * THE source of truth for all visible content on this site.
 *
 * A small LLM call will rewrite this file when the template is instantiated for
 * a specific customer (different brand, industry, copy, services, etc.).
 * Components should NEVER hardcode strings — always import from here.
 *
 * Convention for unknown data: use placeholder strings in [SQUARE BRACKETS].
 * Convention for arrays the customer must fill: export as [] (empty).
 */

export const SITE_TITLE = "Coastal Pro Services";
export const SITE_DESCRIPTION =
  "Reliable pest, lawn, and home services across the North Shore. Smart. Safe. Service.";
export const TAGLINE = "Smart. Safe. Service.";

// Hero copy
export const HERO_HEADLINE_TOP = "Smart. Safe.";
export const HERO_HEADLINE_ACCENT = "Pest Control.";
export const HERO_SUBLINE_PREFIX = "Reliable protection from";
export const HERO_ROTATING_WORDS = [
  "Mosquitoes",
  "Ticks",
  "Ants",
  "Rodents",
  "Termites",
  "Roaches",
  "Spiders",
];
export const HERO_SUBLINE_SUFFIX = "— same-day service across the North Shore.";
export const HERO_CTA_PRIMARY = "Get Protected";
export const HERO_CTA_SECONDARY = "Call Now";

// Social proof
export const RATING_VALUE = "5.0";
export const RATING_COUNT = "237";
export const TRUST_BADGES = [
  "No Contracts",
  "Same-Day Service",
  "Pet & Family Safe",
];

// Marquee ticker
export const TICKER_WORDS = [
  "Mosquitoes",
  "Ticks",
  "Ants",
  "Rodents",
  "Termites",
  "Roaches",
  "Spiders",
  "Wasps",
  "Bed Bugs",
];

// Services
export type Service = {
  id: string;
  name: string;
  description: string;
  icon: string;
};

export const SERVICES: Service[] = [
  {
    id: "service-mosquito",
    name: "Mosquito & Tick Treatment",
    description:
      "Targeted yard treatment that knocks down biting insects and protects your family through the warm months.",
    icon: "leaf",
  },
  {
    id: "service-residential",
    name: "Residential Pest Control",
    description:
      "Quarterly home protection covering ants, spiders, roaches, and seasonal invaders — inside and out.",
    icon: "home",
  },
  {
    id: "service-commercial",
    name: "Commercial Programs",
    description:
      "Discreet, scheduled service plans for restaurants, retail, and offices. Documentation included.",
    icon: "building",
  },
  {
    id: "service-rodent",
    name: "Rodent Control",
    description:
      "Inspection, exclusion, and monitoring to stop mice and rats before they nest in your walls.",
    icon: "shield",
  },
  {
    id: "service-termite",
    name: "Termite Monitoring",
    description:
      "Bait stations and annual inspections that catch termite activity before structural damage starts.",
    icon: "bug",
  },
  {
    id: "service-wildlife",
    name: "Wildlife Removal",
    description:
      "Humane trapping and exclusion for squirrels, raccoons, and other unwelcome attic guests.",
    icon: "paw",
  },
];

// Process / how it works
export type ProcessStep = {
  step: number;
  title: string;
  description: string;
};

export const PROCESS_STEPS: ProcessStep[] = [
  {
    step: 1,
    title: "Free Inspection",
    description:
      "We walk your property, identify pressure points, and recommend the lightest-touch plan that solves the problem.",
  },
  {
    step: 2,
    title: "Targeted Treatment",
    description:
      "Licensed technicians apply pet- and family-safe products only where they're needed. No blanket spraying.",
  },
  {
    step: 3,
    title: "Ongoing Protection",
    description:
      "Seasonal follow-ups keep your property protected year-round. Cancel any time — no contracts.",
  },
];

// About
export const ABOUT_HEADING = "Local pros. Honest work.";
export const ABOUT_BODY = [
  "Coastal Pro Services is a small team of licensed technicians who treat your home the way we'd treat our own. We're independently owned and operated, which means decisions get made by people who actually pick up the phone.",
  "Every job starts with an inspection — not a sales pitch. If you don't need a treatment, we'll tell you. If you do, we'll explain exactly what we're using and why.",
];

// Gallery — file names relative to /public/images/gallery
export const GALLERY_IMAGES: { src: string; alt: string }[] = [];

// Testimonials — EMPTY by default. The customer fills these in after launch.
// Components MUST handle the empty case gracefully (render nothing / hide section).
export type Testimonial = {
  quote: string;
  author: string;
  location?: string;
};

export const TESTIMONIALS: Testimonial[] = [];

// Contact info — use [BRACKET PLACEHOLDERS] when the real value is unknown.
export const PHONE = "[BUSINESS PHONE]";
export const PHONE_DISPLAY = "(516) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS], Long Island, NY";
export const HOURS = "Mon–Fri 7:30AM–6PM · Sat 8AM–2PM";
export const SERVICE_AREAS = ["Nassau County", "Suffolk County"];

// Gallery page headers (GALLERY_IMAGES array is defined above)
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Real jobs, real customers. Tap any photo to see the details.";

// Process page headers (PROCESS_STEPS array is defined above)
export const PROCESS_HEADLINE = "How it works.";
export const PROCESS_SUBLINE  = "From your first call to job-done, here's exactly what to expect — no mystery, no surprises.";

// FAQ page
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

// Service area page
export const SERVICE_AREA_HEADLINE = "Where we work.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned, and proud of it. If your town isn't listed, give us a call — we may still be able to help.";
export const SERVICE_AREA_MAP_EMBED = "";  // Customer adds Google Maps embed URL
export const SERVICE_AREA_CITIES: string[] = [];  // Customer fills in

// Footer
export const FOOTER_TAGLINE = "Premium service. Long Island.";
export const FOOTER_NAV = [
  { label: "Home", href: "/" },
  { label: "Services", href: "/services" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Services", href: "/services" },
  { label: "Gallery", href: "/gallery" },
  { label: "Process", href: "/process" },
  { label: "Service Area", href: "/service-area" },
  { label: "FAQ", href: "/faq" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];
