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
 */

export const SITE_TITLE = "Honest Axle Auto";
export const SITE_DESCRIPTION =
  "Straight diagnostics. Real repairs. No upsell. Family-owned mechanic shop.";
export const TAGLINE = "Diagnose. Fix. Done.";

// Hero — INTENTIONALLY in Inter (not the display stencil). Reads like the
// header of a work order, not a marketing brochure.
export const HERO_REF_CODE = "REF-2026-HAA · ANYTOWN · WORK-ORDER";
export const HERO_HEADLINE_TOP = "HONEST DIAGNOSTICS.";
export const HERO_HEADLINE_ACCENT = "REAL REPAIRS.";
export const HERO_SUBLINE =
  "Family-owned, master-tech-staffed. We tell you what's actually wrong, quote it in writing, and only fix what you approve. No upsell, no surprises.";
export const HERO_CTA_PRIMARY = "Get an Estimate";
export const HERO_CTA_SECONDARY = "See What We Fix";
export const HERO_SERVICE_CHIP = "BRAKES · ENGINE · TRANS · DIAG · TIRES";

// Trust bar — four badges with parts-catalog stamps.
export type TrustBadge = {
  ref: string;
  label: string;
  detail: string;
};

export const TRUST_BADGES: TrustBadge[] = [
  { ref: "BADGE-01", label: "ASE MASTER", detail: "Certified Technicians" },
  { ref: "BADGE-02", label: "BBB ACCREDITED", detail: "[BBB RATING]" },
  { ref: "BADGE-03", label: "[CLUB] APPROVED", detail: "Roadside Network" },
  { ref: "BADGE-04", label: "FAMILY OWNED", detail: "Independent Shop" },
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
    id: "service-brakes",
    ref: "SVC-A47",
    name: "BRAKE SERVICE",
    short: "Pads, rotors, lines, fluid.",
    description:
      "Squealing, grinding, soft pedal, vibration — we diagnose it, show you the worn parts, and quote the actual fix. Pads, rotors, calipers, hydraulic lines, and DOT-rated fluid flush. OEM-equivalent parts unless you ask otherwise.",
    image:
      "https://images.unsplash.com/photo-1632823471565-1ecdf7a6f5d6?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-04812",
  },
  {
    id: "service-engine",
    ref: "SVC-B22",
    name: "ENGINE & DIAGNOSTICS",
    short: "Check-engine lights, misfires, rough idle.",
    description:
      "Modern OBD-II scan tools, live data, and freeze-frame analysis. We read the code, then actually verify the root cause before we replace anything. Tune-ups, coil packs, sensor replacement, timing components, head gaskets — and an honest 'don't fix this' when that's the right call.",
    image:
      "https://images.unsplash.com/photo-1486006920555-c77dcf18193c?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05103",
  },
  {
    id: "service-transmission",
    ref: "SVC-C18",
    name: "TRANSMISSION & DRIVELINE",
    short: "Fluid service, mounts, axles, clutch.",
    description:
      "Slipping, late shifts, leaks under the bell housing — diagnosed properly before anyone says 'rebuild.' Automatic fluid + filter service, manual clutch jobs, CV axles, U-joints, drive shafts, and transfer-case service on 4WD/AWD.",
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
      "We mount and balance any tire you bring in, or quote the brands we trust. Hunter four-wheel alignment with before-and-after printouts. TPMS sensor service. Honest tread-life advice — no scare-selling a new set when rotation is what's needed.",
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
      "Manufacturer-spec intervals using the right viscosity and filter for your specific vehicle. Conventional, synthetic blend, or full synthetic — your choice, our recommendation. We log the service in writing so your records stay clean for warranty and resale.",
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
      "Bring the car (or send us to the lot). We put it on the lift, scan it, road-test it, and hand you a written report on every issue we find — frame, drivetrain, brakes, suspension, electronics. A few hours of our time can save you years of headache.",
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
      "On the lift, scan tool plugged in, road-test if needed. We find the actual root cause, not just the trouble code.",
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
      "Master techs do the work. OEM-equivalent parts by default. We keep the old parts so you can see what came off.",
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
export const ABOUT_HEADING = "INDEPENDENT. INDEPENDENT-MINDED.";
export const ABOUT_BODY = [
  "Honest Axle Auto is a family-owned mechanic shop. We're not a chain, we're not a dealership, and we don't answer to a regional service manager with a parts-quota spreadsheet. We answer to the customer standing at the counter.",
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

// Service area — town list with yellow-bar accent.
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
