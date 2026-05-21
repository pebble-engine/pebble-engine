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

export const SITE_TITLE = "Magnolia Home & Garden";
export const SITE_DESCRIPTION =
  "Landscaping, lawn, and home-care services rooted in the community. Honest service. Grown locally.";
export const TAGLINE = "Honest service. Grown locally.";

// Hero copy
export const HERO_HEADLINE_TOP = "Honest service.";
export const HERO_HEADLINE_ACCENT = "Grown locally.";
export const HERO_SUBLINE_PREFIX = "Thoughtful care for your";
export const HERO_ROTATING_WORDS = [
  "Lawn",
  "Garden",
  "Hedges",
  "Patios",
  "Walkways",
  "Trees",
  "Beds",
];
export const HERO_SUBLINE_SUFFIX = "— tended by neighbors who take pride in their work.";
export const HERO_CTA_PRIMARY = "Get a Free Quote";
export const HERO_CTA_SECONDARY = "Call Us";

// Social proof
export const RATING_VALUE = "5.0";
export const RATING_COUNT = "184";
export const TRUST_BADGES = [
  "No Contracts",
  "Locally Owned",
  "Eco-Friendly",
];

// Marquee ticker
export const TICKER_WORDS = [
  "Lawn Care",
  "Garden Beds",
  "Hedge Trimming",
  "Mulching",
  "Seasonal Cleanups",
  "Pruning",
  "Patio Care",
  "Tree Service",
  "Soil Health",
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
    id: "service-lawn",
    name: "Lawn Care & Mowing",
    description:
      "Weekly or bi-weekly mowing, edging, and trimming that keeps your lawn looking cared for all season long.",
    icon: "leaf",
  },
  {
    id: "service-garden",
    name: "Garden Design & Planting",
    description:
      "Seasonal beds, native plantings, and thoughtful design that fits your home and your sunlight.",
    icon: "home",
  },
  {
    id: "service-hedge",
    name: "Hedge & Tree Pruning",
    description:
      "Clean, even shaping for hedges, ornamentals, and small trees — done at the right time of year for healthy regrowth.",
    icon: "shield",
  },
  {
    id: "service-mulch",
    name: "Mulching & Soil Care",
    description:
      "Fresh mulch, compost top-dress, and soil amendments that feed your beds and hold moisture through summer.",
    icon: "bug",
  },
  {
    id: "service-cleanup",
    name: "Spring & Fall Cleanups",
    description:
      "Full-property cleanup — leaves, debris, bed prep, and pruning — so your yard starts each season fresh.",
    icon: "paw",
  },
  {
    id: "service-hardscape",
    name: "Patio & Walkway Care",
    description:
      "Pressure-washing, joint repair, and seasonal sealing for stone patios, brick walkways, and garden borders.",
    icon: "building",
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
    title: "Free Walk-Through",
    description:
      "We come out, walk the property together, and listen to what you want. No upsell — just an honest plan.",
  },
  {
    step: 2,
    title: "Thoughtful Care",
    description:
      "Our team handles the work the way we'd care for our own yards. We respect your space and clean up before we leave.",
  },
  {
    step: 3,
    title: "Year-Round Partnership",
    description:
      "Seasonal visits keep your property thriving. Pause or cancel any time — we earn each visit, not your signature.",
  },
];

// About
export const ABOUT_HEADING = "Local hands. Honest work.";
export const ABOUT_BODY = [
  "Magnolia Home & Garden is a small, locally-owned team that grew out of a love for working outdoors. We treat your yard the way we'd treat our own — slowly, carefully, and with respect for what's already growing there.",
  "Every job starts with a walk-through, not a sales pitch. If a quick fix is the right answer, we'll say so. If a longer plan makes more sense, we'll explain why — and what it costs — before we touch a thing.",
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
export const PHONE_DISPLAY = "(516) 555-0198";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS], Long Island, NY";
export const HOURS = "Mon–Fri 7AM–5PM · Sat 8AM–2PM";
export const SERVICE_AREAS = ["Nassau County", "Suffolk County"];

// Footer
export const FOOTER_TAGLINE = "Grown locally. Long Island.";
export const FOOTER_NAV = [
  { label: "Home", href: "/" },
  { label: "Services", href: "/services" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Services", href: "/services" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];
