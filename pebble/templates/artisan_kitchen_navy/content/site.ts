// content/site.ts
// Single source of truth for ALL brand content.
// A small LLM call will rewrite this file based on the customer's brief.
// Components import from here — they stay stable; only this file changes per build.

// =====================================================================
// Identity
// =====================================================================
export const SITE_TITLE = "Harbor Light Coffee";
export const SITE_DESCRIPTION =
  "Harbor Light Coffee — a coastal cafe and roastery on the waterfront. Pour-overs, espresso, cold brew, and a short breakfast menu. Roasted by hand, served by the harbor.";
export const TAGLINE = "Roasted by hand. Served by the harbor.";

// Eyebrow chip that sits above the hero headline.
export const HERO_EYEBROW = "Coastal cafe · roastery";

// Hero — two-line headline. Line 1 in deep ink, line 2 in accent color.
export const HERO_HEADLINE_LINE_1 = "Slow mornings,";
export const HERO_HEADLINE_LINE_2 = "saltwater air.";
export const HERO_SUBHEADLINE =
  "Single-origin pour-overs, espresso pulled short and sweet, and a short breakfast menu to eat with the door open. Right on the waterfront, where the gulls and the steam meet.";
export const HERO_CTA_PRIMARY = "See the menu";
export const HERO_CTA_PRIMARY_HREF = "/menu";
export const HERO_CTA_SECONDARY = "Visit us";
export const HERO_CTA_SECONDARY_HREF = "/contact";

// Floating badge anchored to the bottom-left of the hero photo card.
// Use a soft, honest label — NOT a fabricated founding year.
export const HERO_BADGE_TITLE = "Open early";
export const HERO_BADGE_SUBTITLE = "from 6am";

// Hero photo (placeholder — replace per customer)
export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=1600&q=80";

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
    emoji: "☕",
    title: "Single-origin pour-overs",
    description:
      "A small rotating menu of beans we roast ourselves. Hand-poured to order on a Hario V60, brewed slow enough that you can watch the bloom.",
  },
  {
    emoji: "🥐",
    title: "Bakery, not a baker",
    description:
      "Croissants, scones, and a few savory bites from neighbors we trust. We keep the list short so everything is gone by the afternoon.",
  },
  {
    emoji: "🌊",
    title: "Seats by the water",
    description:
      "A long counter at the window, two outdoor benches, and the harbor right there. Wi-Fi works, but the view is the point.",
  },
];

// =====================================================================
// About — square photo left, story right
// =====================================================================
export const ABOUT_EYEBROW = "Our story";
export const ABOUT_HEADLINE = "A small counter on the waterfront";
export const ABOUT_BODY = [
  "Harbor Light Coffee started as a roasting hobby that outgrew the garage. We rent a short, narrow shop on the waterfront with a window that opens onto the slip, a long counter, and an espresso machine that hums all morning.",
  "The menu is small on purpose. We brew what we love, change the beans with what's fresh from the importer, and we're happy to tell you exactly where any of it came from. Pull up a stool, take your time.",
];
export const ABOUT_IMAGE_URL =
  "https://images.unsplash.com/photo-1453614512568-c4024d13c247?auto=format&fit=crop&w=1200&q=80";
export const ABOUT_CTA = "Read more about us";
export const ABOUT_CTA_HREF = "/about";

// =====================================================================
// Menu — filterable categories. The drinks ARE the product.
// =====================================================================
export const MENU_EYEBROW = "On the bar";
export const MENU_HEADLINE = "Today's pour";
export const MENU_INTRO =
  "What we usually have on. The single-origin rotates with the season — we post the day's beans on the chalkboard each morning.";

export const MENU_CATEGORIES = ["All", "Espresso", "Brew", "Bakery", "Breakfast"];

export type MenuItem = {
  id: string;
  name: string;
  description: string;
  price: string;
  category: "Espresso" | "Brew" | "Bakery" | "Breakfast";
  image_url: string;
};

export const MENU_ITEMS: MenuItem[] = [
  {
    id: "espresso",
    name: "Espresso",
    description:
      "Single origin, pulled short and sweet. Ask the barista what we're running this week — the menu changes when the bag does.",
    price: "$3.50",
    category: "Espresso",
    image_url:
      "https://images.unsplash.com/photo-1510707577719-ae7c14805e3a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "cortado",
    name: "Cortado",
    description:
      "Double espresso cut with a small pour of steamed whole milk. Served in a heavy glass, no foam to speak of.",
    price: "$4.75",
    category: "Espresso",
    image_url:
      "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "flat-white",
    name: "Flat White",
    description:
      "Two ristretto shots and silky whole milk, slightly stronger than a latte. The everyday morning cup.",
    price: "$5.25",
    category: "Espresso",
    image_url:
      "https://images.unsplash.com/photo-1517701604599-bb29b565090c?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "pour-over",
    name: "Pour-Over",
    description:
      "Hario V60, brewed to order on the rotating single-origin. Takes about four minutes — worth every one of them.",
    price: "$6",
    category: "Brew",
    image_url:
      "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "cold-brew",
    name: "Cold Brew",
    description:
      "Steeped sixteen hours in cold water, served over ice in a tall glass. Smooth, low-acid, no sweetener needed.",
    price: "$5.50",
    category: "Brew",
    image_url:
      "https://images.unsplash.com/photo-1517959105821-eaf2591984ca?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "drip-coffee",
    name: "Drip Coffee",
    description:
      "Our house blend in a fresh batch every thirty minutes. Free refills if you're sitting in.",
    price: "$3.50",
    category: "Brew",
    image_url:
      "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "butter-croissant",
    name: "Butter Croissant",
    description:
      "Forty-eight hour laminated dough from the bakery up the street. Golden top, hollow bottom, pulls apart like rope.",
    price: "$5",
    category: "Bakery",
    image_url:
      "https://images.unsplash.com/photo-1555507036-ab1f4038808a?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "scone",
    name: "Maple Oat Scone",
    description:
      "Crumbly outside, tender middle, finished with a maple glaze. Best with a cortado.",
    price: "$4.50",
    category: "Bakery",
    image_url:
      "https://images.unsplash.com/photo-1486427944299-d1955d23e34d?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "avocado-toast",
    name: "Avocado Toast",
    description:
      "Sourdough toast, smashed avocado, lemon, chili flake, sea salt. Add a soft-boiled egg for two more.",
    price: "$9",
    category: "Breakfast",
    image_url:
      "https://images.unsplash.com/photo-1525351484163-7529414344d8?auto=format&fit=crop&w=1200&q=80",
  },
  {
    id: "yogurt-bowl",
    name: "Yogurt & Granola",
    description:
      "Whole-milk yogurt, house-made oat granola, seasonal fruit, a drizzle of local honey.",
    price: "$8",
    category: "Breakfast",
    image_url:
      "https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1200&q=80",
  },
];

// =====================================================================
// Contact / hours
// =====================================================================
export const CONTACT_EYEBROW = "Come by";
export const CONTACT_HEADLINE = "Find the cafe";
export const CONTACT_INTRO =
  "We're right on the waterfront, two short blocks from the marina. Tables inside, two benches out front, dogs welcome on a leash.";

export const PHONE = "[BUSINESS PHONE]";
export const EMAIL = "hello@harborlightcoffee.com";
export const ADDRESS_LINE_1 = "[STREET ADDRESS]";
export const ADDRESS_LINE_2 = "On the waterfront";
export const HOURS_LINES = [
  { label: "Mon – Fri", value: "6am – 3pm" },
  { label: "Saturday", value: "7am – 4pm" },
  { label: "Sunday", value: "7am – 2pm" },
  { label: "Holidays", value: "Closed" },
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
  { label: "Wholesale beans", href: "/contact" },
];

export const FOOTER_HOUSE_LINKS = [
  { label: "Our story", href: "/about" },
  { label: "The menu", href: "/menu" },
];

// =====================================================================
// About page extras
// =====================================================================
export const ABOUT_PAGE_HEADLINE = "How Harbor Light Coffee came to be";
export const ABOUT_PAGE_BODY = [
  "We opened in a narrow waterfront shop because we wanted to make the kind of coffee we missed: light enough to taste the bean, patient enough to brew right, served somewhere you'd actually want to sit. The lease was small. The view was big. We loved both immediately.",
  "Today we're still a small crew — two baristas, one roaster, and a rotating cast of friends who help on weekends. We source green coffee from importers we know by name, roast in small batches twice a week, and pour everything you order with care.",
  "If we're out of a particular bean by the time you get here, it usually means tomorrow's roast is going to be a good one. Come back early.",
];

// =====================================================================
// Menu page extras
// =====================================================================
export const MENU_PAGE_HEADLINE = "Everything on the bar";
export const MENU_PAGE_INTRO =
  "We post the day's single-origin on the chalkboard each morning. This is what you can usually expect to find.";

// =====================================================================
// Contact page extras
// =====================================================================
export const CONTACT_PAGE_HEADLINE = "Say hello";
export const CONTACT_PAGE_INTRO =
  "Questions about the menu, wholesale beans, or a quiet weekday morning by the water? Drop us a note — we read every one.";
