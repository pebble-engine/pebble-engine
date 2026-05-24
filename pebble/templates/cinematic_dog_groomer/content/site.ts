export const SITE_TITLE       = "[Your Grooming Co.]";
export const SITE_DESCRIPTION = "Small-batch dog grooming — never crowded, never rushed. We get to know your dog before the clippers come out.";
export const TAGLINE          = "Grooms your dog loves.";
export const PHONE   = "[(555) 555-0100]";
export const EMAIL   = "[hello@example.com]";
export const ADDRESS = "[123 Main St, City, ST 00000]";

export const HERO_BG_IMAGE          = "/hero.jpg";
export const HERO_PILL              = "BOOKING THIS WEEK";
export const HERO_HEADLINE          = "Grooms your dog loves.";
export const HERO_SUBLINE           = "Small-batch appointments — never crowded. We get to know your dog's quirks before the clippers come out. Most pups leave wagging.";
export const HERO_CTA_PRIMARY       = "Book online";
export const HERO_CTA_PRIMARY_HREF  = "/contact";
export const HERO_CTA_SECONDARY     = "See our services";
export const HERO_CTA_SECONDARY_HREF = "/services";

export type Service = { id: string; title: string; description: string; icon: string };
export const SERVICES: Service[] = [
  { id: "svc-1", title: "Full Groom",          description: "Bath, dry, trim, nail grind, ear cleaning, and finish — tailored to your dog's breed and coat type.", icon: "Scissors" },
  { id: "svc-2", title: "Bath & Brush",         description: "Deep clean, conditioning treatment, blow-dry, and brush-out. Perfect for in-between full grooms.",    icon: "Droplets" },
  { id: "svc-3", title: "Anxiety-Friendly",     description: "No cage drying, no rush, no strangers crowding the space. We move at your dog's pace, always.",        icon: "Heart"    },
];

export const ABOUT_PHOTO_IMAGE = "/about.jpg";
export const ABOUT_HEADLINE    = "We're not a factory. We're a salon.";
export const ABOUT_BODY        = "[Two paragraphs about your story — how you got started, what makes you different. Keep it human and specific. Avoid corporate-speak.]";

export type Trust = { label: string; sub: string };
export const TRUST_BADGES: Trust[] = [
  { label: "FEAR-FREE CERT", sub: "Fear Free Certified Professional" },
  { label: "INSURED",        sub: "Up to $[amount]"                  },
  { label: "5-STAR RATED",   sub: "[N]+ Google reviews"              },
  { label: "FAMILY-OWNED",   sub: "Serving [city] since [year]"      },
];

export const TESTIMONIAL_QUOTE  = "[A 1-2 sentence testimonial in your customer's voice. Specific results > generic praise. Include a real first name and last initial.]";
export const TESTIMONIAL_AUTHOR = "[Rachel B.], [City]";

export const CONTACT_HEADLINE = "Ready to book?";
export const CONTACT_BODY     = "Tell us about your dog. We respond within an hour during business hours.";
export const CONTACT_HOURS    = "[Mon–Fri 9am–5pm · Sat 9am–3pm]";

export const CTA_BAND_HEADLINE = "Booking this week.";
export const CTA_BAND_BODY     = "Slots are limited — we keep appointments small so your dog gets our full attention.";
export const CTA_BAND_LABEL    = "Book online";
export const CTA_BAND_HREF     = "/contact";

export const FOOTER_TAGLINE = "Small-batch dog grooming, calm and unrushed.";

// --- Gallery page ---
export const GALLERY_HEADLINE = "Recent work.";
export const GALLERY_SUBLINE  = "Real dogs, real grooms. Tap any photo to see the details.";
export const GALLERY_IMAGES: Array<{ src: string; alt: string; caption?: string }> = [
  { src: "/gallery/01.jpg", alt: "[Dog 1 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/02.jpg", alt: "[Dog 2 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/03.jpg", alt: "[Dog 3 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/04.jpg", alt: "[Dog 4 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/05.jpg", alt: "[Dog 5 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/06.jpg", alt: "[Dog 6 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/07.jpg", alt: "[Dog 7 after groom]",  caption: "[Optional 1-line caption]" },
  { src: "/gallery/08.jpg", alt: "[Dog 8 after groom]",  caption: "[Optional 1-line caption]" },
];

// --- Process page ---
export const PROCESS_HEADLINE = "How it works.";
export const PROCESS_SUBLINE  = "From booking to pickup, here's exactly what to expect — calm, clear, no surprises.";
export type ProcessStep = { number: string; title: string; description: string };
export const PROCESS_STEPS: ProcessStep[] = [
  { number: "01", title: "Book online or by phone", description: "Tell us your dog's breed, coat type, and any sensitivities. We'll match them to the right appointment slot." },
  { number: "02", title: "Drop-off + check-in",     description: "We do a quick nose-to-tail check before we start. You'll know exactly what we'll do and what it costs." },
  { number: "03", title: "Pickup time — they're ready", description: "We text when your dog is done. No waiting around in a crate — we time pickup to when we finish." },
];

// --- FAQ page ---
export const FAQ_HEADLINE = "Common questions.";
export const FAQ_SUBLINE  = "If your question isn't here, just ask — we usually reply within the hour.";
export type FAQItem = { q: string; a: string };
export const FAQ_ITEMS: FAQItem[] = [
  { q: "Is my dog safe here?",              a: "[Yes — we are Fear Free certified, fully insured, and we never use cage dryers. Your dog's comfort comes first.]" },
  { q: "Do you groom cats too?",             a: "[Yes/No — we specialize in dogs, but we do take cats on select days. Ask when you book.]" },
  { q: "How long does a groom take?",        a: "[Typically 1.5–3 hours depending on size, coat type, and services. We never rush.]" },
  { q: "What if my dog has anxiety?",        a: "[Tell us at booking — we're experienced with anxious dogs. We use calming techniques and go at their pace.]" },
  { q: "What forms of payment do you take?", a: "[Cash, check, all major cards. We collect payment at pickup.]" },
  { q: "How often should my dog be groomed?",a: "[Varies by breed — every 4–8 weeks for most dogs. We'll recommend a schedule at your first appointment.]" },
];

// --- Service area page ---
export const SERVICE_AREA_HEADLINE = "Where we work.";
export const SERVICE_AREA_SUBLINE  = "Local, family-owned, and proud of it. If your town isn't listed, give us a call — we may still be able to help.";
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
