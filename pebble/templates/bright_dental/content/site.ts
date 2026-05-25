export const SITE_TITLE       = "[Your Dental Co] | Friendly Family & Pediatric Dentistry";
export const SITE_DESCRIPTION = "Calm, modern dentistry for every age. No upsells. No rushing. Just honest, gentle care.";
export const BRAND_NAME       = "[Your Dental Co]";

export const PHONE      = "[(555) 555-0100]";
export const PHONE_TEL  = "5555550100";
export const EMAIL      = "care@[example].com";
export const ADDRESS    = "[123 Wellness Blvd, Suite 200]";
export const CITY_LINE  = "[City, ST ZIP]";
export const LICENSE    = "[XXXXXX]";

export const TRUSTED_SINCE = "Trusted in [City] since [Year]";

export const HERO_IMAGE    = "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=900&q=80";
export const HERO_HEADLINE = "[Your friendly dental home for every stage of life.]";
export const HERO_SUBHEAD  = "Cleanings that feel calm. Honest answers. Zero pressure. We see kids, teens, adults, and nervous first-timers.";
export const HERO_PRIMARY_CTA = "Book an appointment";
export const HERO_PRIMARY_HREF = "/booking";
export const HERO_SECONDARY_CTA = "See how it works";
export const HERO_SECONDARY_HREF = "/#process";
export const HERO_FOOTNOTE = "Same-day emergency slots available · Most PPO insurance accepted";

export type Service = {
  title: string;
  body:  string;
  icon:  "sparkle" | "smile" | "kid" | "shine" | "clock" | "card";
};

export const SERVICES: Service[] = [
  { icon: "sparkle", title: "Routine Cleanings & Exams", body: "60-minute slots. Deep cleanings, gentle x-rays, and a plan you actually understand." },
  { icon: "smile",   title: "Fillings & Restorations",   body: "Tooth-colored, mercury-free. We match shade, polish smooth, and send you out smiling." },
  { icon: "kid",     title: "Kids & Pediatric Care",     body: "Sticker chart, kid-sized tools, and a team that knows how to sit at eye level and listen." },
  { icon: "shine",   title: "Cosmetic & Whitening",      body: "Veneers, bonding, take-home trays. We show you a preview before we start." },
  { icon: "clock",   title: "Emergency Care",            body: "Broken tooth, sudden pain, knocked-out? We keep same-day slots open daily." },
  { icon: "card",    title: "Flexible Financing",        body: "0% plans for [12] months, HSA/FSA accepted. We break down costs upfront." },
];

export type ProcessStep = {
  step: string;
  title: string;
  body: string;
};

export const PROCESS_STEPS: ProcessStep[] = [
  { step: "1", title: "Book online",                  body: "Pick a date, pick a time. Instant confirmation. Change or cancel anytime with no penalty." },
  { step: "2", title: "First visit: listen, don't rush", body: "We'll review your history, answer every question, and map out a gentle plan. No upselling. Ever." },
  { step: "3", title: "Ongoing care, your pace",       body: "We'll remind you when it's time. You can come in every 3 months or every 6. Your teeth, your rhythm." },
];

export type TeamMember = {
  name: string;
  role: string;
  bio:  string;
  image: string;
  alt: string;
};

export const TEAM: TeamMember[] = [
  {
    name:  "Dr. [Name], DDS",
    role:  "General & Cosmetic Lead · [N] years in practice",
    bio:   "Specializes in anxiety-free sedation and natural-looking restorations. Known for explaining procedures in plain English.",
    image: "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=600&q=80",
    alt:   "Dr. [Surname] portrait",
  },
  {
    name:  "Dr. [Name], DMD",
    role:  "Pediatric & Orthodontics · [N] years in practice",
    bio:   "Former children's hospital clinician. Uses tell-show-do techniques and keeps appointments under 30 minutes for kids.",
    image: "https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=600&q=80",
    alt:   "Dr. [Surname] portrait",
  },
  {
    name:  "[Name], RDH",
    role:  "Lead Hygienist · [N] years in practice",
    bio:   "Gentlest hands on staff. Leads our gum health program and teaches kids how to floss without gagging.",
    image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=600&q=80",
    alt:   "[Name], RDH portrait",
  },
];

export type FAQ = { q: string; a: string };

export const FAQS: FAQ[] = [
  { q: "How much will it cost?",                  a: "Routine cleanings run about [$N–$N] out of pocket. Fillings typically [$N–$N]. We verify your insurance before your visit and give you a clear, itemized estimate in plain dollars. No hidden fees." },
  { q: "Do you accept my insurance?",             a: "We network with most major PPO plans, including [Aetna], [Delta Dental], [Guardian], and [BlueCross BlueShield]. HMO/Medicaid? Call us — we have a referral network for those." },
  { q: "What happens at my kid's first visit?",   a: "We keep it under 25 minutes. Count teeth, check bite, show brushing demos with a mirror. No drills, no pressure. If they're scared, we stop. Seriously." },
  { q: "Do you offer payment plans?",             a: "Yes. 0% financing for up to [12] months through [CareCredit / internal plan]. We also accept HSA/FSA. We'll never start treatment until you approve the payment terms." },
  { q: "I have dental anxiety. Can I still come?", a: "Absolutely. Over [N]% of our patients self-identify as anxious. We offer nitrous, weighted blankets, noise-canceling headphones, and stop-on-command. You're in control." },
];

export const INSURANCE_CARRIERS: string[] = [
  "[Aetna]",
  "[Delta Dental]",
  "[Guardian]",
  "[BlueCross BlueShield]",
  "[Cigna]",
  "[MetLife]",
  "[United Concordia]",
  "[Humana]",
];

export type HoursRow = { day: string; hours: string };

export const HOURS: HoursRow[] = [
  { day: "Mon – Thu", hours: "8:00 AM – 6:00 PM" },
  { day: "Friday",    hours: "8:00 AM – 4:00 PM" },
  { day: "Saturday",  hours: "9:00 AM – 1:00 PM (Emergency only)" },
  { day: "Sunday",    hours: "Closed" },
];

export const TESTIMONIAL_QUOTE = "[I haven't seen a dentist in [N] years because I was terrified. The team at [Your Dental Co] made me feel safe. I actually fell asleep in the chair. I cried a little when it was all done — in the best way.]";
export const TESTIMONIAL_NAME  = "[Ava M.]";
export const TESTIMONIAL_META  = "Patient since [2021]";

export const NAV_LINKS = [
  { label: "Home",            href: "/" },
  { label: "Our Team",        href: "/team" },
  { label: "FAQ & Insurance", href: "/faq" },
];

export const BOOKING_HREF = "/booking";

export const REASON_OPTIONS: string[] = [
  "Routine Cleaning & Exam",
  "Tooth Pain / Sensitivity",
  "Broken / Chipped Tooth",
  "Kids First Checkup",
  "Cosmetic Consult",
  "Other",
];

export const TIME_OPTIONS: Array<{ value: string; label: string }> = [
  { value: "",       label: "Anytime" },
  { value: "am",     label: "Morning (8-11)" },
  { value: "midday", label: "Late Morning (11-1)" },
  { value: "pm",     label: "Afternoon (1-4)" },
  { value: "late",   label: "Evening (4-6)" },
];
