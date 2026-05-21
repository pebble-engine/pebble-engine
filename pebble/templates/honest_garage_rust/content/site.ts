/**
 * THE source of truth for all visible content on this site.
 *
 * A small LLM call will rewrite this file when the template is instantiated for
 * a specific customer (different brand, industry, copy, services, etc.).
 * Components should NEVER hardcode strings — always import from here.
 *
 * Convention for unknown data: use placeholder strings in [SQUARE BRACKETS].
 * Convention for arrays the customer must fill: export as [] (empty).
 *
 * Convention for ref codes (the "parts catalog" DNA signature): every section
 * gets a JetBrains Mono ref code stamp. Pattern is `<DOMAIN>-<INDEX>` or
 * `<DOMAIN>-<NAME>` — e.g. SVC-A47, BADGE-01, IMG-REF-04812. Components read
 * these from here so the customer can re-stamp the site with their own
 * shop-numbering scheme later.
 *
 * Tonal register for this template (honest_garage_rust): vintage-Americana
 * classic-car mechanic. Same work-order voice as honest_garage, different
 * cultural feel — old-school, hands-on, family-trade, neighborhood-shop.
 */

export const SITE_TITLE = "Rust Belt Garage";
export const SITE_DESCRIPTION =
  "Old-school repairs. Real work. Real prices. Classic and modern cars welcome.";
export const TAGLINE = "Old-school repairs. Real work. Real prices.";

// Hero — INTENTIONALLY in Inter (not the display stencil). Reads like the
// header of a work order, not a marketing brochure.
export const HERO_REF_CODE = "REF-2026-RBG · ANYTOWN · WORK-ORDER";
export const HERO_HEADLINE_TOP = "AMERICAN-MADE REPAIRS.";
export const HERO_HEADLINE_ACCENT = "NO SHORTCUTS.";
export const HERO_SUBLINE =
  "Family-owned neighborhood shop. We work on classics and dailies alike — diagnose the real problem, quote it in writing, and only do the work you approve. No upsell, no parts-quota nonsense.";
export const HERO_CTA_PRIMARY = "Get an Estimate";
export const HERO_CTA_SECONDARY = "See What We Fix";
export const HERO_SERVICE_CHIP = "RESTORATION · ENGINE · TRANS · BRAKES · TIRES";

// Trust bar — four badges with parts-catalog stamps.
export type TrustBadge = {
  ref: string;
  label: string;
  detail: string;
};

export const TRUST_BADGES: TrustBadge[] = [
  { ref: "BADGE-01", label: "ASE MASTER", detail: "Certified Technicians" },
  { ref: "BADGE-02", label: "BBB ACCREDITED", detail: "[BBB RATING]" },
  { ref: "BADGE-03", label: "CLASSIC-CAR CLUB", detail: "Approved Shop" },
  { ref: "BADGE-04", label: "FAMILY OWNED", detail: "Independent Garage" },
];

// Services — parts-catalog "directory" with SVC codes.
export type Service = {
  id: string;
  ref: string;
  name: string;
  short: string;
  description: string;
  image: string;
  imageRef: string;
};

export const SERVICES: Service[] = [
  {
    id: "service-restoration",
    ref: "SVC-A47",
    name: "CLASSIC RESTORATION",
    short: "Frame-off, mechanical, or just sort it out.",
    description:
      "Full frame-off or driver-quality mechanical sort. Carburetor rebuilds, points-and-condenser tune-ups, vintage wiring, brake-system conversions, rust repair done the right way. We work on American iron from the muscle era through the 80s — and we don't pretend a Concours job when you wanted a weekender.",
    image:
      "https://images.unsplash.com/photo-1632823471565-1ecdf7a6f5d6?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-04812",
  },
  {
    id: "service-engine",
    ref: "SVC-B22",
    name: "ENGINE & DIAGNOSTICS",
    short: "From small-blocks to OBD-II.",
    description:
      "Old-school compression and vacuum testing on carb'd engines. Modern OBD-II scan tools, live data, and freeze-frame work on anything 1996-up. Tune-ups, coil packs, sensor replacement, timing components, head gaskets — and an honest 'leave it alone' when the gauge isn't lying.",
    image:
      "https://images.unsplash.com/photo-1486006920555-c77dcf18193c?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05103",
  },
  {
    id: "service-transmission",
    ref: "SVC-C18",
    name: "TRANSMISSION & DRIVELINE",
    short: "Manuals, autos, vintage three-speeds.",
    description:
      "Slipping, late shifts, leaks under the bell housing — diagnosed before anyone says 'rebuild.' Manual clutch jobs (modern hydraulic or vintage linkage), automatic fluid + filter service, CV axles, U-joints, drive shafts. Original-spec parts for restorations, OEM-equivalent for dailies.",
    image:
      "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05277",
  },
  {
    id: "service-tires",
    ref: "SVC-D31",
    name: "TIRES & ALIGNMENT",
    short: "Mount, balance, four-wheel alignment.",
    description:
      "We mount and balance whatever you bring in — modern radials, period-correct bias-plies for the classics, whitewalls cleaned up properly. Hunter four-wheel alignment with before-and-after printouts. Honest tread-life advice, no scare-selling a new set when rotation is what's needed.",
    image:
      "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05518",
  },
  {
    id: "service-maintenance",
    ref: "SVC-E04",
    name: "SCHEDULED MAINTENANCE",
    short: "Oil, filters, belts, fluids.",
    description:
      "Manufacturer-spec intervals using the right viscosity and filter for your specific vehicle — straight-weight for the older stuff, full synthetic for the newer. We log the service in writing so your records stay clean for warranty, resale, or that file you keep in the glovebox.",
    image:
      "https://images.unsplash.com/photo-1632823469850-2f77dd9c7f93?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05891",
  },
  {
    id: "service-inspection",
    ref: "SVC-F09",
    name: "PRE-PURCHASE INSPECTION",
    short: "Before you sign anything.",
    description:
      "Bring the car (or send us to the lot — classics included). We put it on the lift, scan it if it'll scan, road-test it, and hand you a written report on every issue we find: frame, drivetrain, brakes, suspension, electronics, rust. A few hours of our time can save you years of headache.",
    image:
      "https://images.unsplash.com/photo-1492144534655-ae79c964c9d7?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-06044",
  },
];

// Process — five-step workflow with ref-coded badges.
export type ProcessStep = {
  step: number;
  ref: string;
  title: string;
  description: string;
};

export const PROCESS_STEPS: ProcessStep[] = [
  {
    step: 1,
    ref: "STEP-01",
    title: "DROP OFF",
    description:
      "Pull in or call ahead. Tell us what you're noticing — sounds, smells, lights, vibration. We log it on the work order.",
  },
  {
    step: 2,
    ref: "STEP-02",
    title: "DIAGNOSE",
    description:
      "On the lift, scan tool or vacuum gauge in hand, road-test if needed. We find the actual root cause, not just the trouble code.",
  },
  {
    step: 3,
    ref: "STEP-03",
    title: "QUOTE",
    description:
      "Written estimate with parts + labor itemized. We call you before any work starts. No surprise charges, ever.",
  },
  {
    step: 4,
    ref: "STEP-04",
    title: "FIX",
    description:
      "Master techs do the work. OEM-equivalent parts by default — original-spec for restorations. We keep the old parts so you can see what came off.",
  },
  {
    step: 5,
    ref: "STEP-05",
    title: "PICKUP",
    description:
      "Final inspection, written invoice, warranty paperwork. We walk you through everything we did, in plain English.",
  },
];

// About — the shop's own story, ref-stamped like a job ticket.
export const ABOUT_REF_CODE = "ABT-DOC-001";
export const ABOUT_HEADING = "INDEPENDENT. NEIGHBORHOOD SHOP.";
export const ABOUT_BODY = [
  "Rust Belt Garage is a family-owned neighborhood shop. We're not a chain, we're not a dealership, and we don't answer to a regional service manager with a parts-quota spreadsheet. We answer to the customer standing at the counter — sometimes that's a guy in coveralls with a 70s Chevelle, sometimes it's a parent in a minivan. Same shop, same standards.",
  "Every job starts with a real diagnosis — not a 'recommended service' list pulled from a maintenance database. If your car doesn't need it, we'll tell you. If it does, we'll show you the worn part on the lift before we order the replacement.",
  "We've been doing this long enough to know the cars worth saving and the ones it's time to walk away from. We'll give you the honest answer either way.",
];

// Gallery — the customer drops their own shop / vehicle photos here.
export const GALLERY_IMAGES: { src: string; alt: string; ref: string }[] = [];

// Testimonials — EMPTY by default. The customer fills these in after launch.
// Components MUST handle the empty case gracefully (render nothing / hide section).
export type Testimonial = {
  quote: string;
  author: string;
  location?: string;
};

export const TESTIMONIALS: Testimonial[] = [];
export const TESTIMONIALS_REF = "REV-SUMMARY";

// Service area — town list with rust-bar accent.
export const SERVICE_AREA_HEADING = "WE COVER";
export const SERVICE_AREAS: string[] = [
  "[CITY ONE]",
  "[CITY TWO]",
  "[CITY THREE]",
  "[CITY FOUR]",
  "[CITY FIVE]",
  "[CITY SIX]",
];

// Contact info — use [BRACKET PLACEHOLDERS] when the real value is unknown.
export const PHONE = "[BUSINESS PHONE]";
export const PHONE_DISPLAY = "(555) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS]";
export const HOURS = "Mon–Fri 7:30AM–6PM · Sat 8AM–2PM · Sun Closed";
export const MAP_REF = "MAP-REF-001";

// Footer
export const FOOTER_TAGLINE = "Independent. Master-tech. Family-owned.";
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
