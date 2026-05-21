// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call rewrites this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.
//
// Convention for unknown data: bracketed placeholders ([BUSINESS PHONE]).
// Convention for arrays the customer must populate: export as [] (empty).

// Brand
export const SITE_TITLE = "Inkhouse Atelier";
export const SITE_DESCRIPTION =
  "Inkhouse Atelier — a Brooklyn tattoo studio for fine-line, blackwork, and custom one-of-one pieces.";
export const TAGLINE = "Marked. Permanent. Yours.";

// Wordmark — split for the navbar + footer (blackletter main + accent eyebrow)
export const WORDMARK_EYEBROW = "EST. BROOKLYN";
export const WORDMARK_MAIN = "Inkhouse";
export const WORDMARK_SECOND = "Atelier";

// Hero — full-bleed video/photo backdrop, giant blackletter wordmark
export const HERO_EYEBROW = "Custom Tattoo Atelier";
export const HERO_HEADLINE_LINE_1 = "Inkhouse";
export const HERO_HEADLINE_LINE_2 = "Atelier";
export const HERO_SUBHEADLINE =
  "Private studio in Brooklyn for fine-line, blackwork, and bespoke custom pieces. By appointment only.";
export const HERO_CTA_PRIMARY = "Book a Consult";
export const HERO_CTA_PRIMARY_HREF = "/contact";
export const HERO_CTA_SECONDARY = "See the Work";
export const HERO_CTA_SECONDARY_HREF = "/gallery";

// Background — a dark cinematic still (Unsplash). The hero <video> element
// falls back to this photo when the source URL is empty / unsupported.
export const HERO_VIDEO_URL =
  "https://cdn.coverr.co/videos/coverr-tattoo-artist-at-work-1574/1080p.mp4";
export const HERO_POSTER_URL =
  "https://images.unsplash.com/photo-1542856391-010fb87dcfed?auto=format&fit=crop&w=2400&q=80";

// THE WORK — gallery preview (carousel-style on homepage)
export const GALLERY_EYEBROW = "The Work";
export const GALLERY_HEADLINE = "A Portfolio in Black & Gold";
export const GALLERY_INTRO =
  "Every piece is drawn for one person. Browse a small selection of recent work below, or book a consult to discuss your own.";

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
    style: "Fine-line",
    image_url:
      "https://images.unsplash.com/photo-1565058379802-bbe93b2f703a?auto=format&fit=crop&w=1200&q=80",
    alt: "Fine-line tattoo on forearm",
  },
  {
    id: "g2",
    title: "Untitled II",
    style: "Blackwork",
    image_url:
      "https://images.unsplash.com/photo-1542727365-19732a80dcfd?auto=format&fit=crop&w=1200&q=80",
    alt: "Blackwork tattoo on shoulder",
  },
  {
    id: "g3",
    title: "Untitled III",
    style: "Illustrative",
    image_url:
      "https://images.unsplash.com/photo-1568515387631-8b650bbcdb90?auto=format&fit=crop&w=1200&q=80",
    alt: "Illustrative tattoo on back",
  },
  {
    id: "g4",
    title: "Untitled IV",
    style: "Fine-line",
    image_url:
      "https://images.unsplash.com/photo-1531884070720-1bd6c64dde85?auto=format&fit=crop&w=1200&q=80",
    alt: "Fine-line tattoo detail",
  },
  {
    id: "g5",
    title: "Untitled V",
    style: "Blackwork",
    image_url:
      "https://images.unsplash.com/photo-1577083287808-1eed6dcd1e0d?auto=format&fit=crop&w=1200&q=80",
    alt: "Blackwork sleeve detail",
  },
  {
    id: "g6",
    title: "Untitled VI",
    style: "Illustrative",
    image_url:
      "https://images.unsplash.com/photo-1611501275019-9b5cda994e8d?auto=format&fit=crop&w=1200&q=80",
    alt: "Illustrative tattoo close-up",
  },
];

// Services — three core service tiers shown on the homepage
export const SERVICES_EYEBROW = "What we do";
export const SERVICES_HEADLINE = "Three Ways to Get Marked";
export const SERVICES: Array<{
  id: string;
  name: string;
  description: string;
}> = [
  {
    id: "custom",
    name: "Custom Pieces",
    description:
      "We sit with you, sketch from scratch, and refine until the design feels permanent before the needle ever touches skin.",
  },
  {
    id: "flash",
    name: "Studio Flash",
    description:
      "Pre-drawn designs from the resident artists. One-of-one — once a flash is claimed, it's never inked again.",
  },
  {
    id: "coverups",
    name: "Cover-Ups & Reworks",
    description:
      "Re-imagining older ink with blackwork, fine-line, or illustrative work. We'll tell you honestly what's possible.",
  },
];

// About — two-column portrait + text block
export const ABOUT_EYEBROW = "The Studio";
export const ABOUT_HEADLINE = "A Private Atelier in Brooklyn";
export const ABOUT_BODY = [
  "Inkhouse Atelier is a small, appointment-only tattoo studio in Brooklyn. We work in fine-line, blackwork, and illustrative styles, and we draw every piece by hand before it ever becomes ink.",
  "Our resident artists trained across editorial illustration, traditional Americana, and contemporary blackwork. We share a bias: a tattoo should outlast the trend that inspired it.",
  "The studio is sterile, single-use, and quiet. No walk-ins, no crowds, no rush — just the two of us in a room, getting it right.",
];
export const ABOUT_PORTRAIT_URL =
  "https://images.unsplash.com/photo-1567532900872-f4e906cbf06a?auto=format&fit=crop&w=1200&q=80";
export const ABOUT_PORTRAIT_ALT = "Inkhouse Atelier studio interior";

// Booking CTA — video-background centered section between content and footer
export const BOOKING_EYEBROW = "Ready when you are";
export const BOOKING_HEADLINE = "Book a Consult";
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
export const HOURS = "Wed–Sat · 12pm–9pm · By appointment";

export const SOCIAL = {
  instagram: "[INSTAGRAM]",
  tiktok: "[TIKTOK]",
};

// Footer column links
export const FOOTER_QUICK_LINKS = [
  { label: "The Studio", href: "/about" },
  { label: "Gallery", href: "/gallery" },
  { label: "Book a Consult", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Gallery", href: "/gallery" },
  { label: "Studio", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// About page
export const ABOUT_PAGE_EYEBROW = "About";
export const ABOUT_PAGE_HEADLINE = "The Studio Behind the Mark";
export const ABOUT_PAGE_INTRO =
  "Inkhouse Atelier was built around a small belief: a tattoo should be a conversation, not a transaction.";

// Gallery page
export const GALLERY_PAGE_EYEBROW = "Portfolio";
export const GALLERY_PAGE_HEADLINE = "The Work";
export const GALLERY_PAGE_INTRO =
  "A rotating selection of recent pieces. To commission your own, start with a consult.";

// Contact page
export const CONTACT_EYEBROW = "Get in touch";
export const CONTACT_HEADLINE = "Book a Consult";
export const CONTACT_INTRO =
  "Send us a note — what you're thinking, where on your body, and any references. We'll reply within two business days.";
