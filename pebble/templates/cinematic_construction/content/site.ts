export const SITE_TITLE       = "[Your Construction Co.]";
export const SITE_DESCRIPTION = "Licensed general contractor. Additions, remodels, new builds. On-time, on-budget, bonded.";
export const TAGLINE          = "Built right. On time.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "NOW BOOKING [SEASON] PROJECTS";
export const HERO_HEADLINE          = "Built right. On time.";
export const HERO_SUBLINE           = "General contractor for additions, remodels, and new builds. Licensed, bonded, and committed to a 4-week max response window on every active site. Fixed bids before we break ground.";
export const HERO_CTA_PRIMARY       = "Request a bid";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See past projects";
export const HERO_CTA_SECONDARY_HREF = "/gallery";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Additions & Remodels",        description: "Kitchen, bath, primary-suite additions. Permits, structural, finishes — single GC, single point of contact, single bid.",                                                                                  icon: "Home"          },
  { id: "svc-2", title: "New Construction",             description: "Ground-up residential builds. Design-build option with our architect, or your plans — either way we run the schedule and the subs.",                                                                       icon: "Hammer"        },
  { id: "svc-3", title: "Commercial Build-Outs",        description: "Tenant improvements, office fit-outs, restaurant + retail. ADA-aware, accustomed to fast-track schedules and after-hours work.",                                                                           icon: "Building2"     },
  { id: "svc-4", title: "Project Management & Permits", description: "Pre-construction services, permit expediting, owner-rep on existing projects. Bring us in early to de-risk the budget.",                                                                                   icon: "ClipboardList" },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Local GC. [N]+ years building in [city].";
export const ABOUT_BODY        = "[Two paragraphs about your company — when you started, the kinds of projects you take, the relationships you've built with subs and inspectors. Lead with the projects you're most proud of and the standards that didn't slip on them.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "GENERAL CONTRACTOR", sub: "License #[number]"         },
  { label: "BONDED",             sub: "$[amount] surety"           },
  { label: "INSURED",            sub: "Up to $[amount] GL"         },
  { label: "LOCAL",              sub: "Building in [city] since [year]" },
];

export const TESTIMONIAL_QUOTE  = "[They handed us the keys 9 days ahead of schedule. The bid was firm, the change orders were minimal, and every subcontractor on site treated our house like it was their own. We'd hire them again tomorrow.]";
export const TESTIMONIAL_AUTHOR = "[The Patel Family], [City]";

export const CONTACT_HEADLINE = "Got a project in mind?";
export const CONTACT_BODY     = "Tell us the scope. We respond within a business day with next steps — typically a site visit and bid timeline.";
export const CONTACT_HOURS    = "[Mon–Fri 7am–5pm · After-hours by appointment]";

export const CTA_BAND_HEADLINE = "Free site assessment.";
export const CTA_BAND_BODY     = "We come out, walk the project, and tell you straight whether your scope and budget line up. No commitment.";
export const CTA_BAND_LABEL    = "Schedule a walk-through";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Licensed GC. Built right in [city].";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent projects.";
export const GALLERY_SUBLINE  = "Additions, new builds, commercial — real projects in [city].";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Project 1]", caption: "[Optional caption]" },
  { src: "/gallery/02.jpg", alt: "[Project 2]", caption: "[Optional caption]" },
  { src: "/gallery/03.jpg", alt: "[Project 3]", caption: "[Optional caption]" },
  { src: "/gallery/04.jpg", alt: "[Project 4]", caption: "[Optional caption]" },
  { src: "/gallery/05.jpg", alt: "[Project 5]", caption: "[Optional caption]" },
  { src: "/gallery/06.jpg", alt: "[Project 6]", caption: "[Optional caption]" },
  { src: "/gallery/07.jpg", alt: "[Project 7]", caption: "[Optional caption]" },
  { src: "/gallery/08.jpg", alt: "[Project 8]", caption: "[Optional caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How we work.";
export const PROCESS_SUBLINE  = "From first call to keys in hand. No surprises, no scope creep.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Tell us the scope",   description: "Call, email, or fill out the form. We respond within a business day. Initial conversation is free."                                                                                                              },
  { number: "02", title: "Site visit + bid",    description: "We walk the site, talk through your goals, and follow up with a firm fixed bid + schedule within [N] business days."                                                                                            },
  { number: "03", title: "Build it right",      description: "Project manager assigned, sub schedule locked. Weekly walkthroughs with you, change orders only when YOU sign off. Backed by our [N]-year workmanship guarantee."                                               },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just call — we respond within a business day.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "How long does it take to get a bid?",  a: "[Typically [N] business days after the site visit. Complex projects may take 2 weeks for full scoping.]"                                                                                       },
  { q: "How do change orders work?",           a: "[Every change order is priced in writing before any added work begins. You sign, we proceed. No exceptions.]"                                                                                  },
  { q: "Are you licensed and insured?",        a: "[Yes — GC license #[number], $[amount] in general liability, $[amount] surety bond.]"                                                                                                         },
  { q: "Do you offer financing?",              a: "[We can introduce you to [financing partner] for renovation loans. Disclosure: we receive no kickback — choose your own lender if you prefer.]"                                                },
  { q: "What's your typical project length?",  a: "[Bath remodels 3-6 weeks, kitchen 6-10 weeks, addition 10-16 weeks, new build 6-12 months — varies by scope, permit cycle, and weather.]"                                                    },
  { q: "Lien releases?",                       a: "[Yes — partial lien waivers from every sub on every progress payment, final unconditional lien releases at closeout.]"                                                                         },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE  = "Where we build.";
export const SERVICE_AREA_SUBLINE   = "Local. If your job is outside our usual radius, call — we'll let you know honestly whether we're the right fit.";
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
