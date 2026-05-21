/**
 * THE source of truth for all visible content on this site.
 *
 * A small LLM call will rewrite this file when the template is instantiated for
 * a specific customer (different brand, industry, copy, courses, etc.).
 * Components should NEVER hardcode strings — always import from here.
 *
 * Convention for unknown data: use placeholder strings in [SQUARE BRACKETS].
 * Convention for arrays the customer must fill: export as [] (empty).
 *
 * Brand placeholder: "Northbound Guide Co" — a generic professional
 * outdoor-adventure brand designed to work for wilderness guiding, backcountry
 * instruction, climbing schools, paddling outfitters, or hunter/angler academies
 * without rewriting any component logic.
 */

export const SITE_TITLE = "Northbound Guide Co";
export const SITE_DESCRIPTION =
  "Wilderness instruction and guided expeditions with structured curriculum, certified guides, and serious outdoor results.";
export const TAGLINE = "Beyond the trail. Beyond the map. Beyond yourself.";

// Hero copy — DNA notes: 4 lines, middle line uses the warm-metal gradient text fill
export const HERO_EYEBROW = "EST. 2019 — CERTIFIED WILDERNESS GUIDE";
export const HERO_HEADLINE_LINE_1 = "EARN";
export const HERO_HEADLINE_LINE_2 = "YOUR";
export const HERO_HEADLINE_LINE_3_GOLD = "OWN";
export const HERO_HEADLINE_LINE_4 = "WAY";
export const HERO_TAGLINE = "STRUCTURED CURRICULUM · CERTIFIED GUIDES · SMALL EXPEDITIONS";
export const HERO_CTA_PRIMARY = "BOOK A COURSE";
export const HERO_CTA_SECONDARY = "VIEW EXPEDITIONS";
export const HERO_VIDEO_URL = "https://videos.pexels.com/video-files/4761711/4761711-hd_1920_1080_25fps.mp4";
export const HERO_VIDEO_POSTER =
  "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2400&q=70";

// Stats — counter-up section
export type Stat = { value: string; label: string };
export const STATS: Stat[] = [
  { value: "500+", label: "Students Guided" },
  { value: "12+", label: "Course Programs" },
  { value: "5+", label: "Years Operating" },
  { value: "100%", label: "Certified Instruction" },
];

// Courses / Classes — the catalog people enroll in (CRITICAL section per DNA)
export type Course = {
  id: string;
  name: string;
  description: string;
  level: "Beginner" | "Intermediate" | "Advanced" | "All Levels";
  duration: string;
  featured?: boolean;
};

export const COURSES: Course[] = [
  {
    id: "backcountry-navigation",
    name: "Backcountry Navigation",
    description:
      "Map, compass, and terrain reading from first principles. Build the confidence to leave the marked trail and route-find through any wilderness.",
    level: "Beginner",
    duration: "8 hours",
  },
  {
    id: "cold-weather-survival",
    name: "Cold-Weather Survival",
    description:
      "Shelter, fire, water, and energy management when the temperature drops. Hands-on practice in real winter conditions with continuous instructor feedback.",
    level: "Intermediate",
    duration: "2 days",
  },
  {
    id: "wilderness-first-aid",
    name: "Wilderness First Aid",
    description:
      "Patient assessment and improvised care for remote environments. Scenario-based work covering trauma, environmental injury, and evacuation decisions.",
    level: "All Levels",
    duration: "16 hours",
    featured: true,
  },
  {
    id: "solo-wilderness-travel",
    name: "Solo Wilderness Travel",
    description:
      "A mentored progression for experienced students moving toward unsupported solo trips. Risk planning, contingency systems, and accountability protocols.",
    level: "Advanced",
    duration: "3 days",
    featured: true,
  },
  {
    id: "guided-overnight",
    name: "Guided Overnight Expedition",
    description:
      "A small-group format (4-6 students) covering the core curriculum in a real backcountry setting. Bring a friend, travel together, learn faster.",
    level: "Beginner",
    duration: "2 days",
  },
  {
    id: "refresher-clinic",
    name: "Refresher Clinic",
    description:
      "A focused half-day clinic for returning students. Re-set fundamentals, address sticky points, leave with a personal practice plan for your next trip.",
    level: "All Levels",
    duration: "4 hours",
  },
];

// Instructor bio (authority signal — major DNA element)
export const INSTRUCTOR_NAME = "[GUIDE NAME]";
export const INSTRUCTOR_TITLE = "Founder & Lead Guide";
export const INSTRUCTOR_IMAGE_URL =
  "https://images.unsplash.com/photo-1551632811-561732d1e306?auto=format&fit=crop&w=1200&q=70";
export const INSTRUCTOR_BIO = [
  "I started Northbound Guide Co because I wanted a place where students learn the right way the first time — no shortcuts, no theatrics, just structured wilderness instruction that builds real competence in real terrain.",
  "Every course I run is the same way I'd teach a family member. Small groups, honest feedback, and a curriculum that earns its name.",
];
export const INSTRUCTOR_CREDENTIALS = [
  "Certified wilderness guide with documented field hours",
  "Wilderness First Responder — recertified annually",
  "Insured and permitted for instruction in this region",
  "Background-checked and references available on request",
];

// Mission / philosophy blockquote
export const MISSION_EYEBROW = "Our Mission";
export const MISSION_QUOTE =
  "We don't sell summits. We build competence — the kind that holds up when the weather turns and the trail disappears. Beyond the trail. Beyond the map. Beyond yourself.";
export const MISSION_BODY =
  "Every Northbound Guide Co student walks off the mountain with measurable improvement and a clear path to the next level. That's the bar. If a course doesn't meet it, we redesign it.";

// Offer / discount banner — flexible CTA section
export const OFFER_HEADING = "First-Time Student Discount";
export const OFFER_BODY =
  "New to the backcountry with us? Your first Backcountry Navigation course is 20% off when you book within 30 days of your first contact. Mention the offer below.";
export const OFFER_CTA = "Claim the Discount";

// Gallery — file names relative to /public/images/gallery
export const GALLERY_IMAGES: { src: string; alt: string }[] = [];

// Testimonials — EMPTY by default (anti-slop). Real quotes only.
export type Testimonial = {
  quote: string;
  author: string;
  course?: string;
};

export const TESTIMONIALS: Testimonial[] = [];

// Contact info — use [BRACKET PLACEHOLDERS] when real value is unknown.
export const PHONE = "[BUSINESS PHONE]";
export const PHONE_DISPLAY = "(207) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS], Bethel, ME";
export const HOURS = "Tue–Fri 9AM–6PM · Sat 7AM–4PM · Sun by appointment";
export const SERVICE_AREAS = ["Western Maine", "White Mountains"];

// Footer
export const FOOTER_TAGLINE = "Beyond the trail. Beyond the map. Beyond yourself.";
export const FOOTER_NAV = [
  { label: "Home", href: "/" },
  { label: "Courses", href: "/courses" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Courses", href: "/courses" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Social links — empty strings are hidden by the Footer
export const SOCIAL = {
  instagram: "",
  facebook: "",
  youtube: "",
};
