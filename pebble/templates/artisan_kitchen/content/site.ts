// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call will rewrite this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.

// =====================================================================
// Identity
// =====================================================================
export const SITE_TITLE = "Maple & Hearth";
export const SITE_DESCRIPTION =
  "Maple & Hearth — a neighborhood bakery and cafe in Greenpoint, Brooklyn. Sourdough, pastries, and slow coffee. Fresh out of the oven, every morning.";
export const TAGLINE = "More than just bread.";

// Eyebrow chip that sits above the hero headline.
export const HERO_EYEBROW = "Neighborhood bakery · cafe";

// Hero — two-line headline. Line 1 in deep ink, line 2 in warm crust.
export const HERO_HEADLINE_LINE_1 = "Slow loaves,";
export const HERO_HEADLINE_LINE_2 = "warm mornings.";
export const HERO_SUBHEADLINE =
  "Sourdough, viennoiserie, and small-batch coffee from a tiny kitchen on the north end of Greenpoint. Stop in, sit down, take a loaf home.";
export const HERO_CTA_PRIMARY = "See the menu";
export const HERO_CTA_PRIMARY_HREF = "/menu";
export const HERO_CTA_SECONDARY = "Visit us";
export const HERO_CTA_SECONDARY_HREF = "/contact";

// Floating badge anchored to the bottom-left of the hero photo card.
// Use a soft, honest label — NOT a fabricated founding year.
export const HERO_BADGE_TITLE = "Baked daily";
export const HERO_BADGE_SUBTITLE = "from 6am";

// Hero photo (placeholder — replace per customer)
export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1600&q=80";

// Small rating chip — empty by default (anti-slop). When provided,
// shape: { stars: "5.0", source: "Google", count: "120+" }
export const HERO_RATING: { stars: string; source: string; count: string } | null =
  null;

// =====================================================================
// Features — three rounded-4xl cards on the alt-cream band
// =====================================================================
export const FEATURES_EYEBROW = "What we do";
export const FEATURES_HEADLINE = "Three things, done well";
export const FEATURES = [
  {
    emoji: "🥖",
    title: "Naturally leavened",
    description:
      "A small starter we keep alive on the back counter. Long ferments, simple flour, salt, water — that is the whole recipe.",
  },
  {
    emoji: "🥐",
    title: "All-butter pastry",
    description:
      "Croissants and pain au chocolat laminated by hand. We bake them off twice a morning so the second tray is just as warm.",
  },
  {
    emoji: "☕",
    title: "Slow coffee",
    description:
      "A single-origin espresso, hand pours over freshly ground beans, and oat milk that tastes like oats — not sugar.",
  },
];

// =====================================================================
// About — square photo left, story right
// =====================================================================
export const ABOUT_EYEBROW = "Our story";
export const ABOUT_HEADLINE = "A small kitchen on a quiet block";
export const ABOUT_BODY = [
  "Maple & Hearth started as a sourdough habit that outgrew the apartment. We rent a narrow storefront in Greenpoint with a wood floor that creaks, a long marble counter, and an oven that throws heat clear across the room.",
  "The menu is short on purpose. We bake what we love, change it with the seasons, and we are happy to tell you exactly how anything was made. Pop in, say hi, take your time.",
];
export const ABOUT_IMAGE_URL =
  "https://images.unsplash.com/photo-1568254183919-78a4f43a2877?auto=format&fit=crop&w=1200&q=80";
export const ABOUT_CTA = "Read more about us";
export const ABOUT_CTA_HREF = "/about";

// =====================================================================
// Menu — filterable categories. The food IS the product.
// =====================================================================
export const MENU_EYEBROW = "On the counter";
export const MENU_HEADLINE = "Today's bake";
export const MENU_INTRO =
  "What we usually have on. Specials change with the seasons — we post the day's bake on the chalkboard each morning.";

export const MENU_CATEGORIES = ["All", "Bread", "Pastry", "Coffee", "Sweets"];

export type MenuItem = {
  id: string;
  name: string;
  description: string;
  price: string;
  category: "Bread" | "Pastry" | "Coffee" | "Sweets";
  image_url: string;
};

export const MENU_ITEMS: MenuItem[] = [
  {
    id: "country-loaf",
    name: "Country Loaf",
    description:
      "Our everyday sourdough — open crumb, blistered crust, mild tang. Whole wheat and bread flour, three-day ferment.",
    price: "$10",
    category: "Bread",
    image_url:
      "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "seeded-rye",
    name: "Seeded Rye",
    description:
      "Caraway, sunflower, and pumpkin seed in a dense rye crumb. Best with butter and a good knife.",
    price: "$11",
    category: "Bread",
    image_url:
      "https://images.unsplash.com/photo-1608198093002-ad4e005484ec?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "olive-fougasse",
    name: "Olive Fougasse",
    description:
      "Leaf-shaped flatbread with castelvetrano olives and rosemary. Pulls apart in long strips.",
    price: "$8",
    category: "Bread",
    image_url:
      "https://images.unsplash.com/photo-1571115332105-fc8e9b3a6e6a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "croissant",
    name: "Butter Croissant",
    description:
      "Forty-eight hour laminated dough, golden top, hollow bottom. Pulls apart like rope.",
    price: "$5",
    category: "Pastry",
    image_url:
      "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "pain-au-chocolat",
    name: "Pain au Chocolat",
    description:
      "Two batons of dark Valrhona inside the same butter dough as the croissant. Eat warm if you can.",
    price: "$5.50",
    category: "Pastry",
    image_url:
      "https://images.unsplash.com/photo-1623334044303-241021148842?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "morning-bun",
    name: "Morning Bun",
    description:
      "Croissant dough rolled with cinnamon sugar and orange zest, baked in a muffin tin until caramelized.",
    price: "$5",
    category: "Pastry",
    image_url:
      "https://images.unsplash.com/photo-1509365465985-25d11c17e812?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "espresso",
    name: "Espresso",
    description:
      "Single origin, pulled short and sweet. Ask the barista what we are running this week.",
    price: "$3.50",
    category: "Coffee",
    image_url:
      "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "cortado",
    name: "Cortado",
    description:
      "Double espresso cut with a small pour of steamed whole milk. Served in a heavy glass.",
    price: "$4.75",
    category: "Coffee",
    image_url:
      "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "olive-oil-cake",
    name: "Olive Oil Cake",
    description:
      "Single-layer cake made with extra-virgin oil and lemon zest. Damp, fragrant, keeps for days.",
    price: "$6",
    category: "Sweets",
    image_url:
      "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "tahini-cookie",
    name: "Tahini Cookie",
    description:
      "Brown butter, dark sugar, a swirl of tahini, and flaky salt on top. Crisp edge, chewy middle.",
    price: "$4",
    category: "Sweets",
    image_url:
      "https://images.unsplash.com/photo-1499636136210-6f4ee915583e?auto=format&fit=crop&w=1200&q=80",
  },
];

// =====================================================================
// Contact / hours
// =====================================================================
export const CONTACT_EYEBROW = "Come by";
export const CONTACT_HEADLINE = "Find the bakery";
export const CONTACT_INTRO =
  "We are on a quiet block at the north end of Greenpoint, about a five-minute walk from the G train. Tables inside, a bench out front, dogs welcome.";

export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "hello@mapleandhearth.com";
export const ADDRESS_LINE_1 = "[STREET ADDRESS]";
export const ADDRESS_LINE_2 = "Greenpoint, Brooklyn, NY";
export const HOURS_LINES = [
  { label: "Tue – Fri", value: "7am – 4pm" },
  { label: "Saturday", value: "8am – 5pm" },
  { label: "Sunday", value: "8am – 3pm" },
  { label: "Monday", value: "Closed" },
];

export const SOCIAL = {
  instagram: "[INSTAGRAM]",
};

// =====================================================================
// Navigation + footer
// =====================================================================
export const NAV_LINKS = [
  { label: "Menu", href: "/menu" },
  { label: "About", href: "/about" },
  { label: "Visit", href: "/contact" },
];

export const FOOTER_VISIT_LINKS = [
  { label: "Hours & address", href: "/contact" },
  { label: "Get in touch", href: "/contact" },
  { label: "Catering", href: "/contact" },
];

export const FOOTER_HOUSE_LINKS = [
  { label: "Our story", href: "/about" },
  { label: "The menu", href: "/menu" },
];

// =====================================================================
// About page extras
// =====================================================================
export const ABOUT_PAGE_HEADLINE = "How Maple & Hearth came to be";
export const ABOUT_PAGE_BODY = [
  "We opened in a narrow storefront on a quiet stretch of Greenpoint because we wanted to make the kind of bread we missed: long-fermented, lightly seeded, and patient. The lease was small. The oven was old. We loved both immediately.",
  "Today we are still a small team — two bakers, a pastry cook, and a rotating cast of friends who help on Saturdays. We mill some of our grain in-house, source dairy from a farm upstate, and bake everything you see on the shelf that morning.",
  "If we are out of something by the time you get here, it usually means tomorrow is going to be a good day. Come back early.",
];

// =====================================================================
// Menu page extras
// =====================================================================
export const MENU_PAGE_HEADLINE = "Everything on the counter";
export const MENU_PAGE_INTRO =
  "We post the day's bake on the chalkboard each morning. This is what you can usually expect to find.";

// =====================================================================
// Contact page extras
// =====================================================================
export const CONTACT_PAGE_HEADLINE = "Say hello";
export const CONTACT_PAGE_INTRO =
  "Questions about the menu, catering for a small event, or a quiet weekday morning? Drop us a note — we read every one.";
