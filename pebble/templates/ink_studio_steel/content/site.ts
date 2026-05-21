// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call rewrites this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.
//
// Convention for unknown data: bracketed placeholders ([BUSINESS PHONE]).
// Convention for arrays the customer must populate: export as [] (empty).

// Brand
export const SITE_TITLE = "Vault Iron Studio";
export const SITE_DESCRIPTION =
  "Vault Iron Studio — a Brooklyn workshop for forged steel, hand-fabricated metalwork, and bespoke heirloom craft.";
export const TAGLINE = "Forged in detail. Built to last.";

// Wordmark — split for the navbar + footer (blackletter main + accent eyebrow)
export const WORDMARK_EYEBROW = "EST. BROOKLYN";
export const WORDMARK_MAIN = "Vault Iron";
export const WORDMARK_SECOND = "Studio";

// Hero — full-bleed video/photo backdrop, giant blackletter wordmark
export const HERO_EYEBROW = "Forged Metal Workshop";
export const HERO_HEADLINE_LINE_1 = "Vault Iron";
export const HERO_HEADLINE_LINE_2 = "Studio";
export const HERO_SUBHEADLINE =
  "A private workshop in Brooklyn for forged steel, hand-fabricated hardware, and bespoke heirloom pieces. By commission only.";
export const HERO_CTA_PRIMARY = "Request a Commission";
export const HERO_CTA_PRIMARY_HREF = "/contact";
export const HERO_CTA_SECONDARY = "See the Work";
export const HERO_CTA_SECONDARY_HREF = "/gallery";

// Background — a dark cinematic still (Unsplash). The hero <video> element
// falls back to this photo when the source URL is empty / unsupported.
export const HERO_VIDEO_URL =
  "https://cdn.coverr.co/videos/coverr-blacksmith-at-work-4856/1080p.mp4";
export const HERO_POSTER_URL =
  "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=2400&q=80";

// THE WORK — gallery preview (carousel-style on homepage)
export const GALLERY_EYEBROW = "The Work";
export const GALLERY_HEADLINE = "A Portfolio in Steel & Brass";
export const GALLERY_INTRO =
  "Every piece is drawn, forged, and finished by hand. Browse a small selection of recent commissions below, or write to us about your own.";

// Gallery items — placeholder Unsplash imagery; the customer replaces these
// with their own portfolio after launch. Six items keeps the homepage strip
// + gallery page comfortable. NEVER invent client names.
export const GALLERY_ITEMS: Array<{
  id: string;
  title: string;
  style: string;
  image_url: string;
  alt: string;
}> = [
  {
    id: "g1",
    title: "Untitled I",
    style: "Forged Steel",
    image_url:
      "https://images.unsplash.com/photo-1565058379802-bbe93b2f703a?auto=format&fit=crop&w=1200&q=80",
    alt: "Forged steel detail",
  },
  {
    id: "g2",
    title: "Untitled II",
    style: "Hand-Fabricated",
    image_url:
      "https://images.unsplash.com/photo-1542727365-19732a80dcfd?auto=format&fit=crop&w=1200&q=80",
    alt: "Hand-fabricated metalwork close-up",
  },
  {
    id: "g3",
    title: "Untitled III",
    style: "Heirloom Hardware",
    image_url:
      "https://images.unsplash.com/photo-1568515387631-8b650bbcdb90?auto=format&fit=crop&w=1200&q=80",
    alt: "Heirloom hardware piece",
  },
  {
    id: "g4",
    title: "Untitled IV",
    style: "Forged Steel",
    image_url:
      "https://images.unsplash.com/photo-1531884070720-1bd6c64dde85?auto=format&fit=crop&w=1200&q=80",
    alt: "Forged steel surface detail",
  },
  {
    id: "g5",
    title: "Untitled V",
    style: "Hand-Fabricated",
    image_url:
      "https://images.unsplash.com/photo-1577083287808-1eed6dcd1e0d?auto=format&fit=crop&w=1200&q=80",
    alt: "Fabricated metal joint detail",
  },
  {
    id: "g6",
    title: "Untitled VI",
    style: "Heirloom Hardware",
    image_url:
      "https://images.unsplash.com/photo-1611501275019-9b5cda994e8d?auto=format&fit=crop&w=1200&q=80",
    alt: "Heirloom hardware close-up",
  },
];

// Services — three core service tiers shown on the homepage
export const SERVICES_EYEBROW = "What we do";
export const SERVICES_HEADLINE = "Three Ways to Commission";
export const SERVICES: Array<{
  id: string;
  name: string;
  description: string;
}> = [
  {
    id: "custom",
    name: "Custom Commissions",
    description:
      "We sit with you, sketch from scratch, and refine until the design feels permanent before steel ever meets fire.",
  },
  {
    id: "studio",
    name: "Studio Editions",
    description:
      "Limited-run pieces from the resident makers. One-of-one — once an edition is claimed, it's never forged again.",
  },
  {
    id: "restoration",
    name: "Restoration & Rework",
    description:
      "Re-imagining older metalwork with hand-forging, fabrication, or refinishing. We'll tell you honestly what's possible.",
  },
];

// About — two-column portrait + text block
export const ABOUT_EYEBROW = "The Studio";
export const ABOUT_HEADLINE = "A Private Workshop in Brooklyn";
export const ABOUT_BODY = [
  "Vault Iron Studio is a small, commission-only workshop in Brooklyn. We work in forged steel, hand-fabricated hardware, and heirloom restoration, and we draw every piece by hand before a single weld is struck.",
  "Our resident makers trained across architectural fabrication, traditional blacksmithing, and contemporary metal craft. We share a bias: a piece of metal should outlast the room it was made for.",
  "The workshop is precise, single-bench, and quiet. No walk-ins, no rush — just the two of us at the anvil, getting it right.",
];
export const ABOUT_PORTRAIT_URL =
  "https://images.unsplash.com/photo-1567532900872-f4e906cbf06a?auto=format&fit=crop&w=1200&q=80";
export const ABOUT_PORTRAIT_ALT = "Vault Iron Studio workshop interior";

// Booking CTA — video-background centered section between content and footer
export const BOOKING_EYEBROW = "Ready when you are";
export const BOOKING_HEADLINE = "Request a Commission";
export const BOOKING_INTRO =
  "Consults are free and last 30–45 minutes. Bring references, half-ideas, or nothing at all.";
export const BOOKING_CTA = "Start the Conversation";
export const BOOKING_CTA_HREF = "/contact";

// Testimonials — EMPTY by default (anti-slop). Real reviews only.
export const TESTIMONIALS: Array<{
  quote: string;
  name: string;
  piece: string;
}> = [];

// Contact / footer
export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS_LINE_1 = "[BUSINESS ADDRESS]";
export const ADDRESS_LINE_2 = "Brooklyn, NY";
export const HOURS = "Wed–Sat · 10am–6pm · By commission";

export const SOCIAL = {
  instagram: "[INSTAGRAM]",
  tiktok: "[TIKTOK]",
};

// Footer column links
export const FOOTER_QUICK_LINKS = [
  { label: "The Studio", href: "/about" },
  { label: "Gallery", href: "/gallery" },
  { label: "Request a Commission", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Gallery", href: "/gallery" },
  { label: "Studio", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// About page
export const ABOUT_PAGE_EYEBROW = "About";
export const ABOUT_PAGE_HEADLINE = "The Workshop Behind the Work";
export const ABOUT_PAGE_INTRO =
  "Vault Iron Studio was built around a small belief: a commission should be a conversation, not a transaction.";

// Gallery page
export const GALLERY_PAGE_EYEBROW = "Portfolio";
export const GALLERY_PAGE_HEADLINE = "The Work";
export const GALLERY_PAGE_INTRO =
  "A rotating selection of recent commissions. To start your own, write to us.";

// Contact page
export const CONTACT_EYEBROW = "Get in touch";
export const CONTACT_HEADLINE = "Request a Commission";
export const CONTACT_INTRO =
  "Send us a note — what you're thinking, where it will live, and any references. We'll reply within two business days.";
