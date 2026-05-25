export const SITE_TITLE       = "[Your Restaurant Name] | Seasonal Dining";
export const SITE_DESCRIPTION = "A celebration of local harvests, seasonal rhythms, and the art of restraint.";
export const BRAND_NAME       = "[Your Restaurant Name]";

export const PHONE      = "[(555) 555-0100]";
export const EMAIL      = "reservations@[example].com";
export const ADDRESS    = "[123 Main St, City, ST]";

export const HERO_IMAGE    = "https://images.unsplash.com/photo-1559339352-11d035aa65de?auto=format&fit=crop&w=1600&q=80";
export const HERO_HEADLINE = "A celebration of local harvests, seasonal rhythms, and the art of restraint.";
export const HERO_PRIMARY_CTA = "Reserve a Table";
export const HERO_PRIMARY_HREF = "/reservations";
export const HERO_SECONDARY_CTA = "View Menu";
export const HERO_SECONDARY_HREF = "/menu";

export const STORY_IMAGE = "https://images.unsplash.com/photo-1550507992-eb63ffeea0e8?auto=format&fit=crop&w=800&q=80";
export const STORY_HEADLINE = "The Philosophy";
export const STORY_P1 = "Our kitchen operates on the principle that the finest ingredients require only a guiding hand. We source exclusively from [Region] producers, allowing the terroir to speak for itself. Every dish is designed to evoke a memory or introduce a new sensation, never to distract.";
export const STORY_P2 = "The dining room is an extension of this ethos: a quiet conviction that luxury lies in simplicity. We invite you to slow down, taste deeply, and experience [Chef Name]'s vision.";

export const GALLERY_IMAGES: Array<{ src: string; alt: string }> = [
  { src: "https://images.unsplash.com/photo-1555396273-af153290246b?auto=format&fit=crop&w=600&q=80", alt: "Dish 1" },
  { src: "https://images.unsplash.com/photo-1514326640560-7d063ef2aed5?auto=format&fit=crop&w=600&q=80", alt: "Dish 2" },
  { src: "https://images.unsplash.com/photo-1550966871-3ed3c47e2ce2?auto=format&fit=crop&w=600&q=80", alt: "Interior 1" },
  { src: "https://images.unsplash.com/photo-1546549032-9571cd6932a2?auto=format&fit=crop&w=600&q=80", alt: "Interior 2" },
  { src: "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=600&q=80", alt: "Dish 3" },
  { src: "https://images.unsplash.com/photo-1559328279-a4c34d97885b?auto=format&fit=crop&w=600&q=80", alt: "Bar area" },
  { src: "https://images.unsplash.com/photo-1582271937850-37d47d6a8371?auto=format&fit=crop&w=600&q=80", alt: "Chef plating" },
  { src: "https://images.unsplash.com/photo-1563245371-24d1f29e5b63?auto=format&fit=crop&w=600&q=80", alt: "Dessert detail" },
];

export const HOURS: Array<{ day: string; hours: string }> = [
  { day: "Monday",               hours: "Closed" },
  { day: "Tuesday",              hours: "5:00 PM – 10:00 PM" },
  { day: "Wednesday – Thursday", hours: "5:00 PM – 10:30 PM" },
  { day: "Friday – Saturday",    hours: "5:00 PM – 11:00 PM" },
  { day: "Sunday",               hours: "4:00 PM – 9:00 PM" },
];

export type MenuItem = {
  name: string;
  description: string;
  price: string;
  tags: string[]; // 'v' | 'gf' | 'df'
};

export type MenuSection = {
  title: string;
  items: MenuItem[];
};

export const MENU_SECTIONS: MenuSection[] = [
  {
    title: "First Course",
    items: [
      { name: "Burrata & Stone Fruit",   description: "Aged balsamic, crushed pistachio",       price: "$24",       tags: ["gf"] },
      { name: "Heirloom Tomato Salad",   description: "Basil oil, aged sherry vinegar",         price: "$19",       tags: ["v", "gf", "df"] },
    ],
  },
  {
    title: "Main Course",
    items: [
      { name: "Duck Breast",             description: "Cherry gastrique, roasted parsnip",      price: "$42",       tags: ["gf", "df"] },
      { name: "Roast Cauliflower",       description: "Harissa, almond, yogurt (add vegan opt)",price: "$32",       tags: ["v", "gf"] },
    ],
  },
  {
    title: "Wine",
    items: [
      { name: "Pinot Noir",              description: "Willamette Valley, 2019",                price: "$18/glass", tags: ["v", "gf", "df"] },
    ],
  },
];

export type Room = {
  id: string;
  title: string;
  image: string;
  capacity: string;
};

export const ROOMS: Room[] = [
  { id: "cellar",  title: "The Cellar",       image: "https://images.unsplash.com/photo-1559328279-a4c34d97885b?auto=format&fit=crop&w=800&q=80", capacity: "12–30 guests" },
  { id: "terrace", title: "The Terrace",      image: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80", capacity: "20–40 guests" },
  { id: "chef",    title: "Chef's Counter",   image: "https://images.unsplash.com/photo-1514326640560-7d063ef2aed5?auto=format&fit=crop&w=800&q=80", capacity: "8–12 guests" },
];

export type JournalPost = {
  date: string;
  title: string;
  body: string;
  image: string;
};

export const JOURNAL_POSTS: JournalPost[] = [
  { date: "March 2026",    title: "The First Asparagus", body: "This year's harvest arrived three days early. We adjusted the opening dish to let the stalks speak.", image: "https://images.unsplash.com/photo-1550507992-eb63ffeea0e8?auto=format&fit=crop&w=600&q=80" },
  { date: "February 2026", title: "Cellar Rotation",     body: "We've retired the 2019 Napa Cabernet and introduced two small-batch Loire whites.",                  image: "https://images.unsplash.com/photo-1546549032-9571cd6932a2?auto=format&fit=crop&w=600&q=80" },
  { date: "January 2026",  title: "Rethinking Fat",      body: "Duck confit preparation has shifted toward rendered fat basting rather than oil submersion.",         image: "https://images.unsplash.com/photo-1559328279-a4c34d97885b?auto=format&fit=crop&w=600&q=80" },
];

export const NAV_LINKS = [
  { label: "Menu",           href: "/menu" },
  { label: "Private Events", href: "/events" },
  { label: "Journal",        href: "/journal" },
];

export const RESERVATION_HREF = "/reservations";
