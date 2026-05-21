// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call will rewrite this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.

// =====================================================================
// Identity
// =====================================================================
export const SITE_TITLE = "Olive Tree Trattoria";
export const SITE_DESCRIPTION =
  "Olive Tree Trattoria — a Mediterranean kitchen and café. Focaccia, bruschetta, olive oil cake, and espresso. Slow food, long lunches, tradition.";
export const TAGLINE = "Slow food. Long lunches. Tradition.";

// Eyebrow chip that sits above the hero headline.
export const HERO_EYEBROW = "Mediterranean trattoria · café";

// Hero — two-line headline. Line 1 in deep ink, line 2 in accent color.
export const HERO_HEADLINE_LINE_1 = "Long lunches,";
export const HERO_HEADLINE_LINE_2 = "olive oil mornings.";
export const HERO_SUBHEADLINE =
  "Stone-baked focaccia, marble-counter bruschetta, and espresso served the way they pour it back home. A small kitchen, an open door, a chair waiting for you.";
export const HERO_CTA_PRIMARY = "See the menu";
export const HERO_CTA_PRIMARY_HREF = "/menu";
export const HERO_CTA_SECONDARY = "Visit us";
export const HERO_CTA_SECONDARY_HREF = "/contact";

// Floating badge anchored to the bottom-left of the hero photo card.
// Use a soft, honest label — NOT a fabricated founding year.
export const HERO_BADGE_TITLE = "Open for pranzo";
export const HERO_BADGE_SUBTITLE = "from 11am";

// Hero photo (placeholder — replace per customer)
export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1600&q=80";

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
    emoji: "🫒",
    title: "Stone-baked focaccia",
    description:
      "Long-rested dough, sea salt, rosemary, and a generous pour of estate olive oil. Baked off twice a day so it's always still warm to the touch.",
  },
  {
    emoji: "🍅",
    title: "Garden bruschetta",
    description:
      "Heirloom tomatoes, torn basil, garlic rubbed on the toast itself. Simple ingredients, picked that morning, dressed at the last minute.",
  },
  {
    emoji: "☕",
    title: "Espresso the right way",
    description:
      "Pulled short, served standing at the bar if you like. A single biscotto on the saucer. No to-go cups before ten.",
  },
];

// =====================================================================
// About — square photo left, story right
// =====================================================================
export const ABOUT_EYEBROW = "Our story";
export const ABOUT_HEADLINE = "A small kitchen, a long table";
export const ABOUT_BODY = [
  "Olive Tree Trattoria started as a Sunday-lunch habit that outgrew the dining room. We took over a narrow storefront with a tile floor, a marble counter, and a brick oven that has not cooled all the way down since we lit it.",
  "The menu is short on purpose. We cook what we love, change it with what's in the market, and we are happy to tell you exactly where any of it came from. Pull up a chair, share a carafe, take your time.",
];
export const ABOUT_IMAGE_URL =
  "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=1200&q=80";
export const ABOUT_CTA = "Read more about us";
export const ABOUT_CTA_HREF = "/about";

// =====================================================================
// Menu — filterable categories. The food IS the product.
// =====================================================================
export const MENU_EYEBROW = "On the table";
export const MENU_HEADLINE = "Today's menù";
export const MENU_INTRO =
  "What we usually have on. Specials change with the season — we post the day's piatti on the chalkboard each morning.";

export const MENU_CATEGORIES = ["All", "Antipasti", "Pasta", "Coffee", "Dolci"];

export type MenuItem = {
  id: string;
  name: string;
  description: string;
  price: string;
  category: "Antipasti" | "Pasta" | "Coffee" | "Dolci";
  image_url: string;
};

export const MENU_ITEMS: MenuItem[] = [
  {
    id: "focaccia",
    name: "Rosemary Focaccia",
    description:
      "Long-rested dough, finished with flaky salt, fresh rosemary, and a generous pour of estate olive oil. Pulls apart in soft, oil-glossed squares.",
    price: "$7",
    category: "Antipasti",
    image_url:
      "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "bruschetta",
    name: "Bruschetta Pomodoro",
    description:
      "Grilled country bread rubbed with garlic, topped with diced heirloom tomato, torn basil, and a drift of olive oil. Eat with your hands.",
    price: "$9",
    category: "Antipasti",
    image_url:
      "https://images.unsplash.com/photo-1572441713132-c542fc4fe282?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "olive-plate",
    name: "Castelvetrano Olives",
    description:
      "Bright green Sicilian olives, cured slow, served at room temperature with a wedge of lemon and warm bread for the oil.",
    price: "$6",
    category: "Antipasti",
    image_url:
      "https://images.unsplash.com/photo-1611171711912-e3a23dee1aab?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "spaghetti-pomodoro",
    name: "Spaghetti al Pomodoro",
    description:
      "Bronze-die spaghetti, slow-cooked tomato sugo, torn basil, a snowfall of parmigiano. The simplest dish on the menu, the hardest to get right.",
    price: "$16",
    category: "Pasta",
    image_url:
      "https://images.unsplash.com/photo-1563379926898-05f4575a45d8?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "cacio-e-pepe",
    name: "Cacio e Pepe",
    description:
      "Tonnarelli, pecorino romano, freshly cracked black pepper, a splash of starchy pasta water. Three ingredients, no shortcuts.",
    price: "$18",
    category: "Pasta",
    image_url:
      "https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "ravioli",
    name: "Ricotta Ravioli",
    description:
      "Hand-folded ravioli filled with fresh sheep's-milk ricotta and lemon zest, finished in brown butter and crisped sage.",
    price: "$19",
    category: "Pasta",
    image_url:
      "https://images.unsplash.com/photo-1587740908075-9e245311c6a8?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "espresso",
    name: "Espresso",
    description:
      "Pulled short and sweet from a small-batch roaster in Naples. Standing at the bar is encouraged.",
    price: "$3.50",
    category: "Coffee",
    image_url:
      "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "cappuccino",
    name: "Cappuccino",
    description:
      "Double espresso, steamed whole milk, a soft cap of foam. Ordered before eleven, no questions asked.",
    price: "$4.75",
    category: "Coffee",
    image_url:
      "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "olive-oil-cake",
    name: "Olive Oil Cake",
    description:
      "Single-layer cake made with the same estate olive oil we cook with, plus lemon zest. Damp, fragrant, keeps for days.",
    price: "$7",
    category: "Dolci",
    image_url:
      "https://images.unsplash.com/photo-1571115764595-644a1f56a55c?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "tiramisu",
    name: "Tiramisù",
    description:
      "Layers of espresso-soaked savoiardi, mascarpone cream, a dusting of dark cocoa. Made fresh each morning and gone by evening.",
    price: "$8",
    category: "Dolci",
    image_url:
      "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=1200&q=80",
  },
];

// =====================================================================
// Contact / hours
// =====================================================================
export const CONTACT_EYEBROW = "Come by";
export const CONTACT_HEADLINE = "Find the trattoria";
export const CONTACT_INTRO =
  "We are on a quiet corner, with tables inside and two under the awning out front. Walk-ins welcome, small parties no problem, dogs on a leash always invited.";

export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "ciao@olivetreetrattoria.com";
export const ADDRESS_LINE_1 = "[STREET ADDRESS]";
export const ADDRESS_LINE_2 = "On the corner";
export const HOURS_LINES = [
  { label: "Tue – Thu", value: "11am – 9pm" },
  { label: "Fri – Sat", value: "11am – 10pm" },
  { label: "Sunday", value: "11am – 8pm" },
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
  { label: "Private dining", href: "/contact" },
];

export const FOOTER_HOUSE_LINKS = [
  { label: "Our story", href: "/about" },
  { label: "The menu", href: "/menu" },
];

// =====================================================================
// About page extras
// =====================================================================
export const ABOUT_PAGE_HEADLINE = "How Olive Tree Trattoria came to be";
export const ABOUT_PAGE_BODY = [
  "We opened in a narrow corner storefront because we wanted to cook the kind of food we missed: long-rested doughs, slow-cooked sugos, espresso pulled the way they pour it back home. The lease was small. The oven was old. We loved both immediately.",
  "Today we are still a small team — two cooks, a pastry hand, and a rotating cast of friends who help on Saturdays. We get our olive oil from a single estate, our flour from a stone-mill upstate, and our tomatoes from whoever is having a good week at the market.",
  "If we are out of a dish by the time you arrive, it usually means tomorrow is going to be a good day. Come back early, share a carafe, stay a while.",
];

// =====================================================================
// Menu page extras
// =====================================================================
export const MENU_PAGE_HEADLINE = "Everything on the table";
export const MENU_PAGE_INTRO =
  "We post the day's piatti on the chalkboard each morning. This is what you can usually expect to find.";

// =====================================================================
// Contact page extras
// =====================================================================
export const CONTACT_PAGE_HEADLINE = "Say hello";
export const CONTACT_PAGE_INTRO =
  "Questions about the menu, a small private dinner, or a long quiet lunch on a weekday? Drop us a note — we read every one.";
