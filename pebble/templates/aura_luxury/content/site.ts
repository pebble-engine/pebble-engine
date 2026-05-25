export const SITE_TITLE       = "AURA | Pristine Luxury Cleaning & Sanitation";
export const SITE_DESCRIPTION = "Surgical-grade residential and commercial restoration cleaning. The standard of untouched precision for estates, penthouses, and corporate spaces.";
export const BRAND_NAME       = "Aura";
export const BRAND_TAGLINE    = "The Standard of Pristine Luxury";

export const PHONE   = "800.555.AURA";
export const EMAIL   = "concierge@aurapristine.com";
export const ADDRESS = "Manhattan · Beverly Hills · Aspen";

export const HERO_IMAGE        = "/penthouse.png";
export const HERO_PILL         = "The Standard of Pristine Luxury";
export const HERO_HEADLINE_1   = "The Luxury of";
export const HERO_HEADLINE_2   = "Untouched";
export const HERO_HEADLINE_3   = "Precision";
export const HERO_BODY         = "For estates, corporate headquarters, and architectural masterpieces that demand surgical attention to detail. We do not just clean. We restore visual purity.";
export const HERO_CTA          = "Secure Your Appointment";
export const HERO_CTA_HREF     = "#services";

export const SPECS: Array<{ label: string; value: string }> = [
  { label: "Particulate Control", value: "HEPA H14 Zero-Tolerance" },
  { label: "Sterilization",       value: "Medical-Grade UV-C" },
  { label: "Surfaces",            value: "Polished to 0.1 Microns" },
  { label: "Air Turnover",        value: "100% HEPA-Filtered" },
  { label: "Agents",              value: "Eco-Lux Non-Toxic" },
];

export const PILLARS: Array<{ icon: string; title: string; body: string }> = [
  { icon: "Sparkles", title: "Micro Detail",   body: "Every surface inspected at 10x magnification." },
  { icon: "Shield",   title: "Surgical Grade", body: "Zero dust residue. Complete sterilization." },
  { icon: "Maximize", title: "White Glove",    body: "Trustworthy, background-checked elite staff." },
];

export const TRANSFORM_IMAGE = "/kitchen.png";
export const TRANSFORM_PILL  = "Visible Metamorphosis";
export const TRANSFORM_TITLE = "The Reveal of Pristine Detail";
export const TRANSFORM_BODY  = "Interact with the slider to witness the surgical removal of dust, residue, and dullness, revealing the high-fidelity, polished surfaces underneath.";
export const TRANSFORM_BEFORE_LABEL = "Before: Dull & Muted";
export const TRANSFORM_AFTER_LABEL  = "After: Sterile Luxury";

export const TRANSFORM_STATS: Array<{ label: string; value: string }> = [
  { label: "Reflective Polish",  value: "99.8% Gloss Index" },
  { label: "Dust Elimination",   value: "0.0% Residual Film" },
  { label: "Sanitization",       value: "Surgical Sterile" },
  { label: "Aromatic Note",      value: "Citrus & Sandalwood" },
];

export type ServiceItem = {
  id: string;
  title: string;
  subtitle: string;
  description: string;
  icon: string;
  duration: string;
  intensity: string;
  span: "wide" | "narrow";
  specs: string[];
};

export const SERVICES: ServiceItem[] = [
  {
    id: "post-construction",
    title: "Post-Construction Clean",
    subtitle: "Architectural Purity",
    description: "Removing fine silica dust, plaster residue, and construction markings to reveal the raw design intent of new architectural builds.",
    icon: "HardHat",
    duration: "12-36 Hours",
    intensity: "Surgical / High",
    span: "wide",
    specs: [
      "3-Phase HEPA dust extraction",
      "Solvent-free adhesive removal",
      "Double-sided exterior/interior glass detail",
      "Deep pore floor scrub & polish",
      "Airborne particulate scrub (4 hours)",
    ],
  },
  {
    id: "luxury-turnover",
    title: "Estate Turnover Service",
    subtitle: "Pristine Occupancy",
    description: "Ultra-detailed preparation of high-end estates for seasonal residents or new ownership transitions.",
    icon: "Compass",
    duration: "8-18 Hours",
    intensity: "Detail Intensive",
    span: "narrow",
    specs: [
      "Tactile surface disinfection",
      "Silk, velvet, and fine drapery dusting",
      "Carrara marble restoration cleaning",
      "Chandelier and crystal detailing",
      "Luxury signature scenting",
    ],
  },
  {
    id: "corporate-sanitation",
    title: "Sanctuary Sanitization",
    subtitle: "Corporate Safe Rooms",
    description: "Clinical-grade disinfection protocols for boardrooms, clean spaces, and executive suites requiring certified pathogen control.",
    icon: "ShieldCheck",
    duration: "4-12 Hours",
    intensity: "Clinical Grade",
    span: "narrow",
    specs: [
      "Electrostatic bio-barrier misting",
      "Active pathogen load validation",
      "HVAC coil & register sterilization",
      "Document archive low-moisture sanitization",
      "Touchpoint thermal imaging sweep",
    ],
  },
  {
    id: "bespoke-archives",
    title: "Bespoke Archive Restoration",
    subtitle: "High-Value Assets",
    description: "Preservation-grade cleaning of private galleries, library archives, collections, and superyachts using museum-approved standards.",
    icon: "FileCheck",
    duration: "Custom Scope",
    intensity: "Restoration Grade",
    span: "wide",
    specs: [
      "Ultra-low moisture micro-vacuuming",
      "Acid-free preservation dusting",
      "UV-inspected organic stain treatment",
      "Custom temperature/humidity monitors",
      "Bonded, certified restoration experts",
    ],
  },
];

export const PHILOSOPHY_QUOTE  = "Cleanliness is not a chore. It is the silent guardian of architectural longevity, the restoration of raw geometry, and the luxury of untouched space.";
export const PHILOSOPHY_AUTHOR = "The Aura Manifesto";

export const LOCATIONS: string[] = ["Manhattan, NY", "Beverly Hills, CA", "Aspen, CO"];

export const FOOTER_BODY = "Surgical sanitization and preservation services for estates, galleries, and high-fidelity corporate assets.";
export const FOOTER_COMPLIANCE = "Fully bonded and insured. Bio-hazard and chemical clean certified. All agents vetted under strict background clearance standards.";
export const FOOTER_RESPONSE   = "Response standard: <15 mins";

export const NAV_LINKS = [
  { label: "Protocols",      href: "#services" },
  { label: "Transformation", href: "#transformation" },
  { label: "Philosophy",     href: "#philosophy" },
  { label: "Inquire",        href: "#inquire" },
];
