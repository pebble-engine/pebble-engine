export const SITE_TITLE       = "[Your Auto Co] | ASE-Certified Independent Auto Repair";
export const SITE_DESCRIPTION = "Honest diagnostics. No upsells. ASE-certified mechanics. Drop-off pricing upfront.";
export const BRAND_NAME       = "[Your Auto Co]";

export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Industrial Blvd, Unit B, City, ST]";

export const HERO_IMAGE     = "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?auto=format&fit=crop&w=1000&q=80";
export const HERO_PILL      = "Independent Shop · ASE Certified";
export const HERO_HEADLINE  = "WE FIX IT RIGHT. THE FIRST TIME.";
export const HERO_BODY      = "No dealership markup. No surprise charges. Just plain diagnostics, honest labor rates, and [Y] years of keeping [City] cars on the road.";
export const HERO_CTA       = "Book Diagnostic";
export const HERO_CTA_HREF  = "#estimate";
export const HERO_EMERG_LABEL = "Call Emerg: [(555) 555-0100]";
export const HERO_EMERG_HREF  = "tel:5555550100";
export const HERO_TECH_LINE = "Lead Tech: [ASE Master Tech: John Smith]";

export type ServicePrice = { name: string; price: string };
export const SERVICES: ServicePrice[] = [
  { name: "Oil Change",            price: "[$45-$85]"        },
  { name: "Brakes & Rotors",       price: "[$120-$280/axle]" },
  { name: "Tire Install / Balance", price: "[$20-$25 per tire]" },
  { name: "AC Repair & Recharge",  price: "[$90-$240]"       },
  { name: "Full Diagnostic",       price: "[$95 FLAT]"       },
  { name: "Transmission Flush",    price: "[$150-$220]"      },
  { name: "Engine Overhaul",       price: "[Call for quote]" },
  { name: "Pre-Purchase Insp.",    price: "[$120]"           },
];

export type TrustPoint = { number: string; title: string; body: string };
export const TRUST_POINTS: TrustPoint[] = [
  { number: "01.", title: "ASE Certified",        body: "Every lead tech holds current [A-Series] certifications. Factory-trained, independent-priced." },
  { number: "02.", title: "[Y]-Year / [N]K Warranty", body: "Parts & labor covered. If it breaks again within warranty, we fix it free. Period." },
  { number: "03.", title: "Zero Upsell Policy",   body: "We only charge for what's broken. If it's safe, we say so. Your call, your budget." },
  { number: "04.", title: "Honest Diagnostic",    body: "$[N] flat fee. Applied directly to your repair cost if you book with us. No blind quotes." },
];

export const BEFORE_AFTER_TITLE = "[Customer Job #0482]";
export const BEFORE_AFTER_PILL  = "Real Work, Real Cars";
export const BEFORE_AFTER_BODY  = "[Engine mount replacement + timing belt kit]. Drag slider to see alignment before vs after torque spec. No filler. Just proper torque specs and OEM parts.";
export const BEFORE_IMAGE = "https://images.unsplash.com/photo-1486262715619-67b85e0b09d3?auto=format&fit=crop&w=800&q=80";
export const AFTER_IMAGE  = "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?auto=format&fit=crop&w=800&q=80";

export type ProcessStep = { number: string; title: string; body: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "1", title: "Drop Off",          body: "Keys in bowl, form signed. We inspect within [2] hours. No waiting bay needed." },
  { number: "2", title: "Diagnose & Call",   body: "We text/call with exact issue + price range. You approve or decline. Zero pressure." },
  { number: "3", title: "Fix & Pickup",      body: "We torque to spec, road test, clean the bay. You get old parts back if requested." },
];

export type Review = { quote: string; author: string };
export const REVIEWS: Review[] = [
  { quote: "[Mechanic called me before touching the car. Explained the leak in plain English. Total was $40 less than dealer quote. They earned a lifer.]",     author: "[Marcus T.] · [2023 Ford F-150]" },
  { quote: "[Third time bringing my Civic here. They don't try to sell me things I don't need. Fast, clean, and the warranty actually means something.]",          author: "[Sarah L.] · [2019 Honda Civic]" },
  { quote: "[Pre-purchase inspection saved me from a nightmare buy. They caught frame rust the dealer missed. Worth every penny for the peace of mind.]",          author: "[David R.] · [Pre-purchase Buyer]" },
  { quote: "[Transmission slipping at 80k. They fixed it same-day, showed me the worn clutch bands, and charged exactly what they quoted upfront. No games.]",     author: "[Jenna K.] · [2016 Toyota RAV4]" },
];

export const REVIEWS_FOOTNOTE = "[N]+ 5-star Google Reviews · [Verified Local]";

export const HOURS: Array<{ days: string; hours: string; closed?: boolean }> = [
  { days: "MON – FRI", hours: "[8:00 AM] – [6:00 PM]" },
  { days: "SATURDAY",  hours: "[9:00 AM] – [2:00 PM]" },
  { days: "SUNDAY",    hours: "CLOSED / TOWING ONLY", closed: true },
];

export const SHOP_BADGES = [
  "AAA Approved Facility",
  "ASE Blue Seal",
  "Free Towing [N] mi radius",
];

export const FOOTER_LINE = "Independent repair since [Year] · [License/Registration # XXXXX]";
export const FOOTER_LEGAL = "Built for [Your Auto Co]. All diagnostic fees subject to vehicle inspection.";

export const NAV_LINKS = [
  { label: "Services", href: "#services" },
  { label: "Process",  href: "#process"  },
  { label: "Reviews",  href: "#reviews"  },
  { label: "Location", href: "#location" },
];
