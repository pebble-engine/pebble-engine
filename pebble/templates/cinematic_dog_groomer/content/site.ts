export const SITE_TITLE       = "[Your Grooming Studio]";
export const SITE_DESCRIPTION = "Stress-free dog grooming. Breed-specific cuts, calm one-on-one room, certified groomer. Pickup texts with photos.";
export const TAGLINE          = "Grooms your dog loves.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "BOOK YOUR FIRST GROOM";
export const HERO_HEADLINE          = "Grooms your dog loves.";
export const HERO_SUBLINE           = "Stress-free baths, breed-specific cuts, and a calm one-on-one room — no kennel anxiety, no rushed groomers. Just a happy dog when you pick them up.";
export const HERO_CTA_PRIMARY       = "Book a groom";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our pups";
export const HERO_CTA_SECONDARY_HREF = "/gallery";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Full Groom",                  description: "Bath, cut to breed standard, nails, ears, paw pads, sanitary trim, bandana on the way out. ~2 hours, one dog at a time.",                                                                                        icon: "Scissors"  },
  { id: "svc-2", title: "Bath & Brush",                 description: "Deep wash, blow-out, brush-out, nails, ears. Great between full grooms or for low-maintenance coats. ~1 hour.",                                                                                                  icon: "Droplets"  },
  { id: "svc-3", title: "De-Shedding & Express Tidy",  description: "Heavy-shedder de-shed package (FURminator + de-shed shampoo). Express tidy for face/feet/sanitary touch-ups between grooms.",                                                                                    icon: "Sparkles"  },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "Certified groomer. Fear-free trained.";
export const ABOUT_BODY        = "[Two paragraphs about you and your studio. Why you went small (vs. big-box grooming). Your training. The kinds of dogs you specialize in. Anything that signals: 'I know dogs, I won't rush yours.']";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "CERTIFIED GROOMER",  sub: "[NCMG / IPG / your cert]" },
  { label: "FEAR-FREE TRAINED",  sub: "Certified handling"        },
  { label: "5-STAR RATED",       sub: "[N]+ Google reviews"       },
  { label: "SMALL STUDIO",       sub: "One dog at a time"         },
];

export const TESTIMONIAL_QUOTE  = "[Our anxious rescue had been kicked out of two other groomers. She came here, did the full groom calmly, and the photo text afterward made me cry. We finally found her person.]";
export const TESTIMONIAL_AUTHOR = "[Sarah K. + Daisy], [City]";

export const CONTACT_HEADLINE = "Ready to book?";
export const CONTACT_BODY     = "Tell us about your dog. First-time grooms include a free consult so we get the cut right.";
export const CONTACT_HOURS    = "[Tue–Sat 9am–5pm · Closed Sun + Mon]";

export const CTA_BAND_HEADLINE = "Open spots this week.";
export const CTA_BAND_BODY     = "First-time groom? We'll text you a confirmation and a 'how it went' photo afterward.";
export const CTA_BAND_LABEL    = "Book a groom";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Small studio. Big love. [City].";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent grooms.";
export const GALLERY_SUBLINE  = "Before-and-afters, breed-specific cuts, fluffy pups in [city].";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Groom 1]", caption: "[Optional caption]" },
  { src: "/gallery/02.jpg", alt: "[Groom 2]", caption: "[Optional caption]" },
  { src: "/gallery/03.jpg", alt: "[Groom 3]", caption: "[Optional caption]" },
  { src: "/gallery/04.jpg", alt: "[Groom 4]", caption: "[Optional caption]" },
  { src: "/gallery/05.jpg", alt: "[Groom 5]", caption: "[Optional caption]" },
  { src: "/gallery/06.jpg", alt: "[Groom 6]", caption: "[Optional caption]" },
  { src: "/gallery/07.jpg", alt: "[Groom 7]", caption: "[Optional caption]" },
  { src: "/gallery/08.jpg", alt: "[Groom 8]", caption: "[Optional caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How your first groom works.";
export const PROCESS_SUBLINE  = "We make first-timers easy. Anxious dog? Just tell us — we work at their pace.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Book + free consult",  description: "Book online or call. First-time grooms include a 15-min consult so we understand your dog's temperament and the cut you want." },
  { number: "02", title: "Drop off + check in",  description: "Drop your pup off at the agreed time. We text you when the groom starts and if anything comes up mid-session."                 },
  { number: "03", title: "Pickup with photos",   description: "Pickup window confirmed by text + a 'how it went' photo so you know what to expect. We talk through next visit's schedule."   },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "My dog is anxious — can you handle her?",  a: "[Yes. Fear-free trained, one dog at a time, no other dogs visible. We work at her pace and can split sessions if needed.]"                                                                    },
  { q: "What breeds do you specialize in?",         a: "[All breeds. Particular experience with [list 3-4 breeds you know well — doodles, poodles, terriers, double-coated etc.].]"                                                                  },
  { q: "What about matted coats?",                  a: "[Charged hourly for severe matting. We'll never shave-down without calling you first to discuss options.]"                                                                                    },
  { q: "Do you need vaccination records?",          a: "[Yes — current rabies and distemper. Send them ahead via email so we have them on file before the first appointment.]"                                                                       },
  { q: "Drop-off and pick-up windows?",             a: "[Drop off 9-10am, pickup 2-4 hours later depending on service. We don't board — dogs go home as soon as they're ready.]"                                                                    },
  { q: "Walk-ins?",                                 a: "[Not for full grooms (we book one dog at a time). Nail trims and express tidies sometimes — call ahead.]"                                                                                    },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE  = "Where we serve.";
export const SERVICE_AREA_SUBLINE   = "Local studio. [City] and surrounding areas. Mobile grooming is on our roadmap — not yet.";
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
