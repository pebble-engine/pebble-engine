export const SITE_TITLE       = "[Your Plumbing Co.]";
export const SITE_DESCRIPTION = "Licensed local plumbers. Same-day emergency response. Up-front pricing on every job.";
export const TAGLINE          = "Pipes fixed. Right. Today.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "24/7 EMERGENCY SERVICE";
export const HERO_HEADLINE          = "Pipes fixed. Right. Today.";
export const HERO_SUBLINE           = "Burst pipes, slow drains, water heater out — call any time. Licensed plumber dispatched within the hour. Up-front pricing before any work starts.";
export const HERO_CTA_PRIMARY       = "Call now";
export const HERO_CTA_PRIMARY_HREF  = "tel:[(555) 555-0100]";
export const HERO_CTA_SECONDARY     = "Book online";
export const HERO_CTA_SECONDARY_HREF = "/contact";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Emergency Repairs",     description: "Burst pipes, no hot water, sewer backups. 24/7 dispatch, technician on-site within the hour in most of [city].", icon: "Siren"   },
  { id: "svc-2", title: "Drain & Sewer",         description: "Clogged drains, slow toilets, sewer-line camera inspection + hydro-jetting. We find the cause, not just the symptom.", icon: "Pipette" },
  { id: "svc-3", title: "Water Heater Service",  description: "Tank or tankless, install or repair. Same-day water-heater replacement available. Most major brands stocked on the truck.", icon: "Flame"   },
  { id: "svc-4", title: "Repipe & Remodel",      description: "Full or partial repipe. Bathroom + kitchen remodel plumbing. Licensed for new-construction permits in [city].", icon: "Wrench"  },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Master plumber. [N]+ years in [city].";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Mention your license #, the neighborhoods you've worked in, the kind of jobs you take pride in. Keep it human.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "MASTER PLUMBER", sub: "License #[number]"          },
  { label: "INSURED",        sub: "Up to $[amount]"            },
  { label: "5-STAR RATED",   sub: "[N]+ Google reviews"        },
  { label: "24/7 EMERGENCY", sub: "Same-day in most of [city]" },
];

export const TESTIMONIAL_QUOTE  = "[Pipe burst at 11pm on a Sunday — they were here in 40 minutes, fixed it, and the price was exactly what they quoted on the phone. Best plumber we've ever called.]";
export const TESTIMONIAL_AUTHOR = "[Maria T.], [City]";

export const CONTACT_HEADLINE = "Need a plumber now?";
export const CONTACT_BODY     = "Call [(555) 555-0100] for emergencies. Otherwise drop us a line — we respond within the hour during business hours.";
export const CONTACT_HOURS    = "[24/7 emergency · Office Mon–Fri 7am–6pm]";

export const CTA_BAND_HEADLINE = "Got a leak right now?";
export const CTA_BAND_BODY     = "Don't let a small drip flood your home. Same-day appointments still open this week.";
export const CTA_BAND_LABEL    = "Call now: [(555) 555-0100]";
export const CTA_BAND_HREF     = "tel:[(555) 555-0100]";

export const FOOTER_TAGLINE = "Licensed plumbers. 24/7 in [city].";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Pipe repairs, water-heater swaps, repipes — real jobs in [city].";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Plumbing job 1]",  caption: "[Optional caption]" },
  { src: "/gallery/02.jpg", alt: "[Plumbing job 2]",  caption: "[Optional caption]" },
  { src: "/gallery/03.jpg", alt: "[Plumbing job 3]",  caption: "[Optional caption]" },
  { src: "/gallery/04.jpg", alt: "[Plumbing job 4]",  caption: "[Optional caption]" },
  { src: "/gallery/05.jpg", alt: "[Plumbing job 5]",  caption: "[Optional caption]" },
  { src: "/gallery/06.jpg", alt: "[Plumbing job 6]",  caption: "[Optional caption]" },
  { src: "/gallery/07.jpg", alt: "[Plumbing job 7]",  caption: "[Optional caption]" },
  { src: "/gallery/08.jpg", alt: "[Plumbing job 8]",  caption: "[Optional caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How a service call works.";
export const PROCESS_SUBLINE  = "From your first call to job-done. Up-front pricing, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Call or book online",   description: "Tell us what's going on. We give a rough quote on the phone so you know what to expect." },
  { number: "02", title: "We diagnose on-site",   description: "Licensed plumber arrives in marked truck. We diagnose the real problem and quote the fix before we touch a wrench." },
  { number: "03", title: "We fix it. Guaranteed.", description: "Most repairs done same visit. Backed by our [N]-year workmanship guarantee — if it leaks again, we come back free." },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common plumbing questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "Do you charge for estimates?",       a: "[Diagnostic visit is $[amount], waived if you book the repair. Phone estimates are always free for common jobs.]" },
  { q: "Are you licensed and insured?",      a: "[Yes — master plumber license #[license number], insured up to $[amount].]" },
  { q: "How fast can you respond?",          a: "[Most of [city] within 60 minutes for true emergencies (burst pipe, no water, sewer backup). Standard calls 1-2 business days.]" },
  { q: "What about after-hours rates?",      a: "[Nights, weekends, and holidays carry a $[amount] dispatch fee on top of the labor rate. Quoted up front.]" },
  { q: "Do you do tankless water heaters?",  a: "[Yes — install, repair, descale. Most major brands. Same-day swap usually possible.]" },
  { q: "What areas do you serve?",           a: "[See our service area page for the full list. Generally within [N] miles of [city].]" },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE = "Where we serve.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned. If your town isn't listed, call — we may still come out.";
export const SERVICE_AREA_MAP_EMBED = "";
export const SERVICE_AREA_CITIES: string[] = [];

export const NAV_LINKS = [
  { label: "Services",     href: "/services"     },
  { label: "Gallery",      href: "/gallery"      },
  { label: "Process",      href: "/process"      },
  { label: "Service Area", href: "/service-area" },
  { label: "FAQ",          href: "/faq"          },
  { label: "About",        href: "/about"        },
  { label: "Contact",      href: "/contact"      },
];
