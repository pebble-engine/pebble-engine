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

export const SITE_TITLE = "Foxtrot Motor Works";
export const SITE_DESCRIPTION =
  "Disciplined repairs. Operational standards. Diesel, fleet, and heavy-duty mechanic shop.";
export const TAGLINE = "Disciplined repairs. Operational standards.";

// Hero — INTENTIONALLY in Inter (not the display stencil). Reads like the
// header of a work order, not a marketing brochure.
export const HERO_REF_CODE = "REF-2026-FMW · SECTOR 04 · WORK-ORDER";
export const HERO_HEADLINE_TOP = "MISSION-READY DIAGNOSTICS.";
export const HERO_HEADLINE_ACCENT = "OPERATIONAL REPAIRS.";
export const HERO_SUBLINE =
  "Veteran-led, master-tech-staffed. We run a checklist, document the findings, and only execute repairs you've signed off on. Diesel, gas, fleet, and heavy-duty — held to military-spec standards.";
export const HERO_CTA_PRIMARY = "Request a Work Order";
export const HERO_CTA_SECONDARY = "See What We Service";
export const HERO_SERVICE_CHIP = "DIESEL · FLEET · BRAKES · DRIVELINE · DIAG";

// Trust bar — four badges with parts-catalog stamps.
export type TrustBadge = {
  ref: string;
  label: string;
  detail: string;
};

export const TRUST_BADGES: TrustBadge[] = [
  { ref: "BADGE-01", label: "ASE MASTER", detail: "Certified Technicians" },
  { ref: "BADGE-02", label: "DIESEL CERTIFIED", detail: "Medium & Heavy-Duty" },
  { ref: "BADGE-03", label: "DOT INSPECTION", detail: "Authorized Facility" },
  { ref: "BADGE-04", label: "VETERAN OWNED", detail: "Independent Shop" },
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
    id: "service-diesel",
    ref: "SVC-A47",
    name: "DIESEL ENGINE SERVICE",
    short: "Powerstroke, Cummins, Duramax — diagnosed properly.",
    description:
      "Light-duty through medium-duty diesel. Injector diagnostics, EGR/DPF service, turbo and intercooler work, fuel-system pressure testing, regen support, and emissions troubleshooting. We document every reading and only authorize what the data supports.",
    image:
      "https://images.unsplash.com/photo-1632823471565-1ecdf7a6f5d6?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-04812",
  },
  {
    id: "service-fleet",
    ref: "SVC-B22",
    name: "FLEET MAINTENANCE",
    short: "Preventive schedules. Detailed records. Scheduled downtime.",
    description:
      "Per-vehicle PM intervals, DVIR-aligned inspection sheets, brake & tire wear tracking, and digital service history exportable for audits. Pickups, vans, box trucks, and light commercial. We schedule the work around YOUR route, not ours.",
    image:
      "https://images.unsplash.com/photo-1486006920555-c77dcf18193c?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05103",
  },
  {
    id: "service-heavy-duty",
    ref: "SVC-C18",
    name: "HEAVY-DUTY DRIVELINE",
    short: "Differentials, transfer cases, U-joints, axles.",
    description:
      "Heavy-duty 4WD/AWD systems serviced to OEM torque specs. Differential fluid + setup, transfer-case rebuilds, U-joint and CV replacement, drive-shaft balancing. Common Powerstroke, Cummins, and Duramax driveline failures handled in-house.",
    image:
      "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05277",
  },
  {
    id: "service-brakes",
    ref: "SVC-D31",
    name: "BRAKE & SUSPENSION",
    short: "Heavy-duty pads, hydraulic lines, air systems.",
    description:
      "Pads, rotors, calipers, hydraulic lines, and DOT-rated fluid service. Heavy-duty and air-assisted brake systems supported. Suspension diagnostics for loaded fleet vehicles — leaf springs, U-bolts, sway bars, and shock service to spec.",
    image:
      "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05518",
  },
  {
    id: "service-maintenance",
    ref: "SVC-E04",
    name: "SCHEDULED MAINTENANCE",
    short: "Oil, filters, fluids, glow plugs — to mil-spec intervals.",
    description:
      "Manufacturer-spec intervals using the right viscosity and filter for your vehicle. Diesel oil services (CK-4, FA-4), fuel filters, glow plugs, coolant flushes, and DEF system service. Every service logged in writing so your maintenance record stays audit-ready.",
    image:
      "https://images.unsplash.com/photo-1632823469850-2f77dd9c7f93?auto=format&fit=crop&w=1400&q=70",
    imageRef: "IMG-REF-05891",
  },
  {
    id: "service-inspection",
    ref: "SVC-F09",
    name: "DOT & PRE-PURCHASE INSPECTION",
    short: "Before you sign — before you roll.",
    description:
      "DOT annual inspections at an authorized facility. Pre-purchase inspections for fleet acquisitions and personal heavy-duty vehicles: frame, drivetrain, brakes, emissions, electronics. You get a written report on every finding, ranked by severity. A few hours of our time can save the operation.",
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
    title: "INTAKE",
    description:
      "Pull in or call ahead. Tell us what you're noticing — sounds, smells, codes, performance. We log it on the work order with timestamps.",
  },
  {
    step: 2,
    ref: "STEP-02",
    title: "INSPECT",
    description:
      "On the lift. Scan tool plugged in. Road-test if needed. We find the actual root cause, not just the trouble code. Every reading documented.",
  },
  {
    step: 3,
    ref: "STEP-03",
    title: "REPORT",
    description:
      "Written estimate with parts + labor itemized. We call before any work starts. No surprise charges. Findings ranked by severity so you can triage.",
  },
  {
    step: 4,
    ref: "STEP-04",
    title: "EXECUTE",
    description:
      "Master techs do the work. OEM-equivalent parts by default. We keep the old parts so you can verify what came off. Torque values to spec, every time.",
  },
  {
    step: 5,
    ref: "STEP-05",
    title: "RELEASE",
    description:
      "Final inspection, written invoice, warranty paperwork. We walk you through everything we did, in plain English. Records archived for your maintenance file.",
  },
];

// About — the shop's own story, ref-stamped like a job ticket.
export const ABOUT_REF_CODE = "ABT-DOC-001";
export const ABOUT_HEADING = "DISCIPLINED. INDEPENDENT. ACCOUNTABLE.";
export const ABOUT_BODY = [
  "Foxtrot Motor Works is a veteran-owned mechanic shop built on the standards we learned in service: document everything, follow the checklist, never skip a step. We're not a chain, not a dealership, and we don't answer to a regional service manager with a parts-quota spreadsheet. We answer to the operator standing at the counter.",
  "Every job starts with a real diagnosis — not a 'recommended service' list pulled from a maintenance database. If your vehicle doesn't need it, we'll tell you. If it does, we'll show you the worn part on the lift and the data behind the call before we order the replacement.",
  "Diesel, gas, fleet, and heavy-duty. We've serviced enough rigs to know the ones worth saving and the ones it's time to walk away from. We'll give you the honest answer either way — backed by paperwork.",
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

// Service area — town list with safety-orange bar accent.
export const SERVICE_AREA_HEADING = "OPERATIONAL SECTORS";
export const SERVICE_AREAS: string[] = [
  "[SECTOR ONE]",
  "[SECTOR TWO]",
  "[SECTOR THREE]",
  "[SECTOR FOUR]",
  "[SECTOR FIVE]",
  "[SECTOR SIX]",
];

// Contact info — use [BRACKET PLACEHOLDERS] when the real value is unknown.
export const PHONE = "[BUSINESS PHONE]";
export const PHONE_DISPLAY = "(555) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS]";
export const HOURS = "Mon–Fri 0700–1800 · Sat 0800–1400 · Sun Closed";
export const MAP_REF = "MAP-REF-001";

// Footer
export const FOOTER_TAGLINE = "Veteran-led. Master-tech. Fleet-capable.";
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
