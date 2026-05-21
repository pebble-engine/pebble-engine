// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call will rewrite this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.

export const SITE_TITLE = "Rose & Veil Apothecary";
export const SITE_DESCRIPTION =
  "Rose & Veil Apothecary — warm, multicultural luxury beauty. Haircare, skincare, and rituals, gently composed by hand.";
export const TAGLINE = "Warm luxury. Made with care.";

// Pinyon Script cursive sub-wordmark sitting above the main wordmark in the navbar
export const WORDMARK_EYEBROW = "Rose & Veil";
export const WORDMARK_MAIN = "Apothecary";

// Hero
export const HERO_HEADLINE = "Where Beauty Feels Like Home";
export const HERO_SUBHEADLINE =
  "A warm atelier of luxury haircare, skincare, and quiet rituals — composed for every shade, every texture, every softening story.";
export const HERO_SCRIPT_ACCENT = "softly, for you";
export const HERO_CTA_PRIMARY = "Shop the Collection";
export const HERO_CTA_PRIMARY_HREF = "/shop";
export const HERO_CTA_SECONDARY = "Our Story";
export const HERO_CTA_SECONDARY_HREF = "/about";
export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1522335789203-aaa9d8e2bd55?auto=format&fit=crop&w=1600&q=80";

// Value pillars — three things this brand stands for
export const VALUES_EYEBROW = "Our promise";
export const VALUES_HEADLINE = "Beauty held with care";
export const VALUES = [
  {
    title: "Multicultural",
    description:
      "Formulas developed and tested across the full spectrum of skin tones and hair textures, because beauty was never one shade.",
  },
  {
    title: "Cruelty-Free",
    description:
      "Leaping Bunny certified. No animal testing — anywhere in our supply chain, ever, full stop.",
  },
  {
    title: "Ethically Sourced",
    description:
      "Botanicals traded at a fair wage, packaging in post-consumer glass, and a carbon-aware logistics partner on every shipment.",
  },
];

// Category grid (2x2)
export const CATEGORIES_EYEBROW = "The collection";
export const CATEGORIES_HEADLINE = "Small things, gently composed";
export const CATEGORIES_SCRIPT_ACCENT = "with love in every detail";
export const PRODUCT_CATEGORIES = [
  {
    id: "haircare",
    name: "Haircare",
    description: "Treatments, oils, and rituals for every texture and coil pattern.",
    image_slot: "haircare",
    image_url:
      "https://images.unsplash.com/photo-1626015449832-583cb74e8d10?auto=format&fit=crop&w=1200&q=80",
    href: "/shop?category=haircare",
  },
  {
    id: "skincare",
    name: "Skincare",
    description: "Serums, balms, and cleansers formulated by chemists, finished by hand.",
    image_slot: "skincare",
    image_url:
      "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=1200&q=80",
    href: "/shop?category=skincare",
  },
  {
    id: "tools",
    name: "Styling Tools",
    description: "Heat tools, brushes, and combs engineered for the long, tender ritual.",
    image_slot: "tools",
    image_url:
      "https://images.unsplash.com/photo-1522337660859-02fbefca4702?auto=format&fit=crop&w=1200&q=80",
    href: "/shop?category=tools",
  },
  {
    id: "fragrance",
    name: "Fragrance",
    description: "Eaux and balm-perfumes composed in small batches, drawn from real botanicals.",
    image_slot: "fragrance",
    image_url:
      "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=1200&q=80",
    href: "/shop?category=fragrance",
  },
];

// Editorial section — magazine-style block
export const EDITORIAL_EYEBROW = "The atelier";
export const EDITORIAL_HEADLINE = "A warm studio in SoHo, a quiet story in every bottle";
export const EDITORIAL_SCRIPT_ACCENT = "made by hand, slowly";
export const EDITORIAL_BODY =
  "Every Rose & Veil formulation begins on a warm bench in our SoHo atelier — botanicals weighed by the gram, tested across textures and tones, softened until they feel like something you'd reach for first thing in the morning. We name nothing finished until the people who will wear it tell us it feels like theirs.";
export const EDITORIAL_BODY_2 =
  "The studio is open to visitors by appointment. Bring questions, your routine, or a friend; leave with a recommendation written in our own hand.";
export const EDITORIAL_IMAGE_URL =
  "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?auto=format&fit=crop&w=1600&q=80";
export const EDITORIAL_CTA = "Book an appointment";
export const EDITORIAL_CTA_HREF = "/contact";

// Featured products — EMPTY by default (anti-slop). Add real products to render the section.
export const FEATURED_PRODUCTS: Array<{
  id: string;
  name: string;
  category: string;
  price: string;
  image_url: string;
  href: string;
}> = [];

// Testimonials — EMPTY by default (anti-slop). Real customer quotes only.
export const TESTIMONIALS: Array<{
  quote: string;
  name: string;
  location: string;
}> = [];

// Contact / footer
export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS_LINE_1 = "[BUSINESS ADDRESS]";
export const ADDRESS_LINE_2 = "SoHo, New York, NY";
export const HOURS = "Tue–Sun 11am–7pm · Closed Mondays";

export const SOCIAL = {
  instagram: "[INSTAGRAM]",
  tiktok: "[TIKTOK]",
  pinterest: "[PINTEREST]",
};

// Footer column linking
export const FOOTER_SHOP_LINKS = [
  { label: "Haircare", href: "/shop?category=haircare" },
  { label: "Skincare", href: "/shop?category=skincare" },
  { label: "Tools", href: "/shop?category=tools" },
  { label: "Fragrance", href: "/shop?category=fragrance" },
];
export const FOOTER_HOUSE_LINKS = [
  { label: "Our story", href: "/about" },
  { label: "The atelier", href: "/about#atelier" },
  { label: "Contact", href: "/contact" },
];
export const FOOTER_HELP_LINKS = [
  { label: "Shipping", href: "/contact" },
  { label: "Returns", href: "/contact" },
  { label: "FAQ", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Shop", href: "/shop" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// About page
export const ABOUT_EYEBROW = "Our story";
export const ABOUT_HEADLINE = "Beauty, the way it was always meant to feel";
export const ABOUT_SCRIPT_ACCENT = "from the very first day";
export const ABOUT_BODY = [
  "Rose & Veil Apothecary began as a question: why does luxury beauty so rarely arrive shaped for the people who actually wear it? We started small — a chemist, an editor, and a stylist sharing one warm bench in SoHo — and built the brand we wished already existed.",
  "Today we formulate, test, and finish every product in that same atelier. Our team is multicultural by design and the formulas reflect that — soft performance across the full range of skin tones, hair textures, and rituals.",
  "We're not in a rush. Each release is a small batch. Each product is named only once the people we trust tell us it feels finished. That, to us, is luxury.",
];

// Shop page header
export const SHOP_EYEBROW = "The collection";
export const SHOP_HEADLINE = "The full atelier";
export const SHOP_INTRO =
  "Browse by category. Every product is formulated and finished by hand in our SoHo studio.";

// Contact page
export const CONTACT_EYEBROW = "Say hello";
export const CONTACT_HEADLINE = "We'd love to hear from you";
export const CONTACT_INTRO =
  "Questions about a product, a routine, or visiting the atelier? Write to us — we read every note, and we always write back.";
