// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call will rewrite this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.

export const SITE_TITLE = "Willow & Slate Estates";
export const SITE_DESCRIPTION =
  "Willow & Slate Estates — boutique brokerage for the Hudson Valley. Quiet places, considered properties.";
export const TAGLINE = "Quiet places. Considered properties.";

// Wordmark — the navbar logo is an 8x8 deep-sage square mark + uppercase wordmark.
export const WORDMARK_MARK = "W"; // single character rendered inside the accent square
export const WORDMARK_MAIN = "Willow & Slate";

// Hero
export const HERO_EYEBROW = "Boutique brokerage";
export const HERO_HEADLINE_LINE_1 = "FIND YOUR";
export const HERO_HEADLINE_LINE_2 = "QUIET ACRE";
export const HERO_SUBHEADLINE =
  "A small bench of advisors representing the Hudson Valley — farmhouses, river estates, and walled gardens from Cold Spring to Hudson — where every acquisition is private, deliberate, and quietly done.";
export const HERO_CTA_PRIMARY = "View Inventory";
export const HERO_CTA_PRIMARY_HREF = "#listings";
export const HERO_CTA_SECONDARY = "Speak Privately";
export const HERO_CTA_SECONDARY_HREF = "/contact";
export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?auto=format&fit=crop&w=1920&q=80";
export const HERO_SCROLL_LABEL = "SCROLL";

// Intro / precision statement — the two-col split text + 2x2 stat grid.
export const INTRO_HEADLINE_LINE_1 = "CONSIDERED";
export const INTRO_HEADLINE_LINE_2 = "GROUND.";
export const INTRO_BODY =
  "We don't list. We curate. Each property under our mark is selected for the buyer it already belongs to — and shown only to the small circle who could plausibly own it. That's the brokerage. That's the bench.";

// Stats — empty by default for honesty (no invented numbers).
// Populate when the customer can substantiate.
export const STATS: Array<{ value: string; label: string }> = [];

// Featured collection — the listings grid. EMPTY by default (anti-slop).
// Never invent properties, addresses, or prices.
export const LISTINGS_EYEBROW = "Featured collection";
export const LISTINGS_HEADLINE_LINE_1 = "PRIVATE";
export const LISTINGS_HEADLINE_LINE_2 = "INVENTORY";
export const LISTINGS_CTA = "View Full Inventory";
export const LISTINGS_CTA_HREF = "/contact";
export const LISTINGS: Array<{
  id: string;
  name: string;
  location: string;
  beds: string;
  baths: string;
  price: string;
  image_url: string;
  badge: "Exclusive" | "New" | "Pending" | null;
  href: string;
}> = [];

// Agent / principal pinned section.
export const PRINCIPAL_EYEBROW = "Principal";
export const PRINCIPAL_NAME_LINE_1 = "PRINCIPAL";
export const PRINCIPAL_NAME_LINE_2 = "INTRODUCTION";
export const PRINCIPAL_BODY =
  "Willow & Slate was founded as a deliberately small bench. We don't operate by volume; we operate by trust. Every introduction is hand-warmed, every showing is by appointment, and every contract is read across a kitchen table — never across a portal.";
// Empty by default until the customer supplies a real headshot + bio.
export const PRINCIPAL_IMAGE_URL = "";
export const PRINCIPAL_STATS: Array<{ value: string; label: string }> = [];

// Contact section — confidential inquiry pill + form.
export const CONTACT_PILL = "Confidential inquiries";
export const CONTACT_HEADLINE_LINE_1 = "SECURE YOUR";
export const CONTACT_HEADLINE_LINE_2 = "ACQUISITION";
export const CONTACT_INTRO =
  "Tell us what you're looking for. A principal will reply within one business day. Discretion is the floor, not a feature.";
export const CONTACT_CTA = "Initiate Inquiry";

// Contact details
export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS_LINE_1 = "[BUSINESS ADDRESS]";
export const ADDRESS_LINE_2 = "Hudson, NY";
export const HOURS = "Mon–Sat 9am–7pm · Sunday by appointment";

export const SOCIAL = {
  instagram: "[INSTAGRAM]",
  linkedin: "[LINKEDIN]",
};

// Navigation
export const NAV_LINKS = [
  { label: "Inventory", href: "/#listings" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Footer legal links — three-part horizontal footer.
export const FOOTER_LEGAL_LINKS = [
  { label: "Terms", href: "/contact" },
  { label: "Privacy", href: "/contact" },
  { label: "Accessibility", href: "/contact" },
  { label: "Fair Housing", href: "/contact" },
];

// About page
export const ABOUT_EYEBROW = "The brokerage";
export const ABOUT_HEADLINE_LINE_1 = "WE ARE";
export const ABOUT_HEADLINE_LINE_2 = "A BENCH.";
export const ABOUT_BODY = [
  "Willow & Slate was assembled on the principle that boutique brokerage is not a size — it is a posture. We say no to listings every week so that the inventory we represent is exactly what we'd want our own families to live in.",
  "Our advisors live where they work. They walk the orchards at Cold Spring in October, drive the back roads of Columbia County in March, and know which stonemason in Rhinebeck answers the phone on a Sunday. That isn't an expertise you can scale.",
  "We are not the largest brokerage in the valley, and we will never try to be. Every transaction we close is one we hand-shepherded from the first cup of coffee to the closing-day key exchange.",
];

// Contact page header
export const CONTACT_PAGE_EYEBROW = "Begin";
export const CONTACT_PAGE_HEADLINE_LINE_1 = "PRIVATE";
export const CONTACT_PAGE_HEADLINE_LINE_2 = "AUDIENCE.";
export const CONTACT_PAGE_INTRO =
  "A principal will reply within one business day. We treat every conversation as a confidence — full stop.";
