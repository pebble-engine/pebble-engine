export const SITE_TITLE       = "[Your HVAC Co.]";
export const SITE_DESCRIPTION = "Licensed HVAC contractor. Same-day repair, full system installs, financing available.";
export const TAGLINE          = "Cool air. On demand.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "FINANCING AVAILABLE";
export const HERO_HEADLINE          = "Cool air. On demand.";
export const HERO_SUBLINE           = "Same-day AC repair, full system installs, and maintenance plans that catch problems before they cost you. Up-front pricing on every visit.";
export const HERO_CTA_PRIMARY       = "Get a free quote";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "Call 24/7";
export const HERO_CTA_SECONDARY_HREF = "tel:[(555) 555-0100]";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "AC Repair",              description: "Same-day diagnostics, parts on the truck for most major brands. Honest quote before we start the wrench.",                                                                     icon: "Snowflake"    },
  { id: "svc-2", title: "Heating & Furnace",      description: "Gas, electric, heat pumps. Annual tune-ups + emergency repair when winter hits at the worst time.",                                                                              icon: "Flame"        },
  { id: "svc-3", title: "New System Installation", description: "High-efficiency systems sized for your home, with rebate paperwork handled for you. Financing available on systems over $[amount].",                                             icon: "PackagePlus"  },
  { id: "svc-4", title: "Maintenance Plans",       description: "Two visits a year, priority dispatch, no overtime fees. Catch the $200 fix before it’s a $5,000 replacement.",                                                             icon: "CalendarCheck" },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local HVAC techs. [N]+ years in [city].";
export const ABOUT_BODY        = "[Two paragraphs about your story — when you started, the brands you specialize in, what sets your crew apart. Keep it human, specific to your region.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "LICENSED HVAC", sub: "License #[number]"         },
  { label: "NATE CERTIFIED", sub: "Technicians"              },
  { label: "5-STAR RATED",  sub: "[N]+ Google reviews"       },
  { label: "FINANCING",     sub: "On qualifying systems"     },
];

export const TESTIMONIAL_QUOTE  = "[AC died on the hottest day of July. They were here in two hours, fixed the capacitor, and the bill matched the phone quote exactly. No upsell, no nonsense.]";
export const TESTIMONIAL_AUTHOR = "[James M.], [City]";

export const CONTACT_HEADLINE = "Ready for cool air?";
export const CONTACT_BODY     = "Tell us what’s going on. We respond within the hour during business hours, 24/7 for true emergencies.";
export const CONTACT_HOURS    = "[Mon–Sat 7am–7pm · 24/7 emergency]";

export const CTA_BAND_HEADLINE = "AC running hot this summer?";
export const CTA_BAND_BODY     = "Same-day diagnostic visits available. Don’t wait for it to fully die.";
export const CTA_BAND_LABEL    = "Schedule a tune-up";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Licensed HVAC. Same-day in [city].";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "AC installs, furnace swaps, ductwork — real jobs in [city].";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[HVAC job 1]", caption: "[Optional caption]" },
  { src: "/gallery/02.jpg", alt: "[HVAC job 2]", caption: "[Optional caption]" },
  { src: "/gallery/03.jpg", alt: "[HVAC job 3]", caption: "[Optional caption]" },
  { src: "/gallery/04.jpg", alt: "[HVAC job 4]", caption: "[Optional caption]" },
  { src: "/gallery/05.jpg", alt: "[HVAC job 5]", caption: "[Optional caption]" },
  { src: "/gallery/06.jpg", alt: "[HVAC job 6]", caption: "[Optional caption]" },
  { src: "/gallery/07.jpg", alt: "[HVAC job 7]", caption: "[Optional caption]" },
  { src: "/gallery/08.jpg", alt: "[HVAC job 8]", caption: "[Optional caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How a service call works.";
export const PROCESS_SUBLINE  = "From your first call to job-done. Up-front pricing, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Call or book online",     description: "Tell us what’s going on. We give a rough estimate on the phone so you know what to expect."                                      },
  { number: "02", title: "We diagnose on-site",     description: "Licensed tech arrives in a marked truck. We diagnose the real problem and quote the fix before any work begins."                       },
  { number: "03", title: "We fix it. Guaranteed.",  description: "Most repairs done same visit. Backed by our [N]-year parts + labor guarantee."                                                         },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common HVAC questions.";
export const FAQ_SUBLINE  = "If your question isn’t here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "What does a diagnostic visit cost?", a: "[$[amount], waived if you book the repair. Free phone estimates for common jobs.]"                                                                                            },
  { q: "Are you licensed and insured?",      a: "[Yes — HVAC contractor license #[number], insured up to $[amount].]"                                                                                                    },
  { q: "What brands do you service?",        a: "[Trane, Carrier, Lennox, Goodman, Rheem, and all major brands. Specialty equipment may take an extra day for parts.]"                                                         },
  { q: "Do you offer financing?",            a: "[Yes — 0% APR for 12 months on qualifying systems through [financing partner]. Quick online application.]"                                                               },
  { q: "What about rebates?",                a: "[We handle the rebate paperwork for you — utility company, manufacturer, and federal energy-efficiency credits where applicable.]"                                        },
  { q: "What areas do you serve?",           a: "[See our service area page. Generally within [N] miles of [city].]"                                                                                                           },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE  = "Where we serve.";
export const SERVICE_AREA_SUBLINE   = "Local HVAC. If your town isn’t listed, call — we may still come out.";
export const SERVICE_AREA_MAP_EMBED = "";   // Customer adds Google Maps embed URL
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
