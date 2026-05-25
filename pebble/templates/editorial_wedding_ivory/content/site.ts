export const SITE_TITLE       = "Ivory & Brass Studio | Daylight Wedding Photography";
export const SITE_DESCRIPTION = "Soft, sunlit editorial wedding photography for the modern couple. Cathedral light, daylight ceremonies, ivory-and-brass craft.";
export const BRAND_NAME       = "Ivory & Brass";

export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "hello@[example].com";
export const ADDRESS = "Based in [City], available worldwide.";

export const HERO_IMAGE     = "https://images.unsplash.com/photo-1511285560982-6517533604a8?auto=format&fit=crop&w=1600&q=80";
export const HERO_HEADLINE  = "Love stories, rendered in light and quiet.";
export const HERO_CTA       = "View our work";
export const HERO_CTA_HREF  = "#featured";

export type StorySlide =
  | { kind: "intro"; label: string; couple: string; venue: string; quote: string; image: string }
  | { kind: "photo"; alt: string; image: string }
  | { kind: "outro"; quote: string; subline: string };

export const FEATURED_SLIDES: StorySlide[] = [
  {
    kind: "intro",
    label: "Featured Story",
    couple: "[Sarah & James]",
    venue: "June 2024, [Venue Name]",
    quote: "[They wanted the day to feel like a dinner party with their favorite people. We let the light guide us.]",
    image: "https://images.unsplash.com/photo-1591604466107-ec97de423991?auto=format&fit=crop&w=800&q=80",
  },
  { kind: "photo", alt: "Getting ready", image: "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=1200&q=80" },
  { kind: "photo", alt: "First look",     image: "https://images.unsplash.com/photo-1511285560982-6517533604a8?auto=format&fit=crop&w=1200&q=80" },
  { kind: "photo", alt: "Ceremony",       image: "https://images.unsplash.com/photo-1469371670807-013ccf25f16a?auto=format&fit=crop&w=1200&q=80" },
  { kind: "photo", alt: "Portraits",      image: "https://images.unsplash.com/photo-1520854221256-17451cc330e7?auto=format&fit=crop&w=1200&q=80" },
  { kind: "outro", quote: "“Stay for the in-between.”", subline: "[View full gallery →]" },
];

export type GalleryItem = { image: string; couple: string; meta: string };

export const GALLERY: GalleryItem[] = [
  { image: "https://images.unsplash.com/photo-1583939003579-730e3918a45a?auto=format&fit=crop&w=600&q=80", couple: "[Mia & Leo]",     meta: "[Venue] · Oct 2024" },
  { image: "https://images.unsplash.com/photo-1532712938310-34cb3a59e8a5?auto=format&fit=crop&w=600&q=80", couple: "[Chloe & Sam]",   meta: "[Venue] · Aug 2023" },
  { image: "https://images.unsplash.com/photo-1537639829272-292388d03098?auto=format&fit=crop&w=600&q=80", couple: "[Elena & David]", meta: "[Venue] · Sep 2024" },
  { image: "https://images.unsplash.com/photo-1519225427870-b68f291d5236?auto=format&fit=crop&w=600&q=80", couple: "[Jules & Remy]",  meta: "[Venue] · May 2023" },
  { image: "https://images.unsplash.com/photo-1606800052052-a08af83e1092?auto=format&fit=crop&w=600&q=80", couple: "[Nora & Alex]",   meta: "[Venue] · Jul 2025" },
  { image: "https://images.unsplash.com/photo-1510076857177-4288b9719796?auto=format&fit=crop&w=600&q=80", couple: "[Tara & Ben]",    meta: "[Venue] · Nov 2024" },
  { image: "https://images.unsplash.com/photo-1522673607918-61d320d79e37?auto=format&fit=crop&w=600&q=80", couple: "[Grace & Tom]",   meta: "[Venue] · Apr 2024" },
  { image: "https://images.unsplash.com/photo-1465495976277-4384d1b7d465?auto=format&fit=crop&w=600&q=80", couple: "[Lily & Mark]",   meta: "[Venue] · Jun 2023" },
  { image: "https://images.unsplash.com/photo-1594855299003-53b31859f658?auto=format&fit=crop&w=600&q=80", couple: "[Maya & Cole]",   meta: "[Venue] · Sep 2023" },
];

export const ABOUT_IMAGE    = "https://images.unsplash.com/photo-1554048612-387768271646?auto=format&fit=crop&w=800&q=80";
export const ABOUT_KICKER   = "The Photographer";
export const ABOUT_HEADLINE = "Why I love this work";
export const ABOUT_QUOTE    = "Weddings move fast, but the moments that matter are quiet. A hand finding a hand. A deep breath before walking down the aisle. I don't direct. I watch. I wait for the frame that tells the truth.";
export const ABOUT_BODY     = "I've spent [N] years documenting love stories across [N]+ states. My kit is always minimal. My style is always natural. If you want candid, cinematic, and completely unhurried — we'll get along.";

export type Package = {
  title: string;
  price: string;
  duration: string;
  features: string[];
  popular?: boolean;
};

export const PACKAGES: Package[] = [
  {
    title: "Elopement",
    price: "$[X],XXX",
    duration: "Starting price · up to [4] hours",
    features: ["[300] edited high-res images", "Online private gallery", "Print release"],
  },
  {
    title: "Full Day",
    price: "$[X],XXX",
    duration: "Starting price · [8-10] hours",
    features: [
      "[700]+ edited high-res images",
      "Second shooter included",
      "Engagement session guide",
      "Heirloom USB + Online Gallery",
    ],
    popular: true,
  },
  {
    title: "Two-Day Celebration",
    price: "$[X],XXX",
    duration: "Starting price · Welcome + Wedding Day",
    features: [
      "Full documentation of both events",
      "Second shooter both days",
      "Printed photo essay booklet",
    ],
  },
];

export type ProcessStep = { number: string; title: string; body: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Inquire",      body: "Tell us your date, venue, and a little about you. I'll reply within [48] hours." },
  { number: "02", title: "Consult Call", body: "We jump on a video or phone call. No pressure. We align on your vision." },
  { number: "03", title: "Engagement",   body: "We meet for a casual shoot. It's about comfort, not perfect poses." },
  { number: "04", title: "Wedding Day",  body: "I arrive early, shoot quietly, and capture the day as it naturally unfolds." },
];

export type Testimonial = { quote: string; author: string };
export const TESTIMONIALS: Testimonial[] = [
  { quote: "[Working with [Your Studio Name] felt like having a quiet witness to our best day. Every photo feels like a memory you can hold. We cried when we saw them.]", author: "[Sarah & Michael], [Venue Name]" },
  { quote: "[They didn't just take pictures; they captured the way my dad laughed when he thought no one was looking. Pure, unscripted magic.]",                         author: "[Elena & Thomas], [Venue Name]" },
  { quote: "[If you want stiff poses and checklist shots, look elsewhere. If you want your actual love story in film-like tones, book them. Today.]",                    author: "[Jules & Remy], [Venue Name]" },
];

export const INSTAGRAM_GRID = [
  "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=200&q=80",
  "https://images.unsplash.com/photo-1465495976277-4384d1b7d465?auto=format&fit=crop&w=200&q=80",
  "https://images.unsplash.com/photo-1520854221256-17451cc330e7?auto=format&fit=crop&w=200&q=80",
  "https://images.unsplash.com/photo-1511285560982-6517533604a8?auto=format&fit=crop&w=200&q=80",
  "https://images.unsplash.com/photo-1594855299003-53b31859f658?auto=format&fit=crop&w=200&q=80",
];

export const NAV_LINKS = [
  { label: "Work",       href: "#featured" },
  { label: "About",      href: "#about" },
  { label: "Investment", href: "#packages" },
  { label: "Kind Words", href: "#testimonials" },
];
