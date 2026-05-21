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
 * Brand placeholder: "Veridian Executive Coaching" — a generic professional
 * coaching/advisory brand designed to work for executive coaches, leadership
 * consultants, communication trainers, professional-services advisors, and
 * other white-collar instructor-led businesses without rewriting any
 * component logic.
 */

export const SITE_TITLE = "Veridian Executive Coaching";
export const SITE_DESCRIPTION =
  "Executive coaching and leadership development with a structured curriculum, senior practitioners, and measurable outcomes.";
export const TAGLINE = "Clarity. Strategy. Results.";

// Hero copy — DNA notes: 4 lines, middle line uses gold-gradient text fill
export const HERO_EYEBROW = "EST. 2019 — SENIOR EXECUTIVE COACH";
export const HERO_HEADLINE_LINE_1 = "BECOME";
export const HERO_HEADLINE_LINE_2 = "THE";
export const HERO_HEADLINE_LINE_3_GOLD = "LEADER";
export const HERO_HEADLINE_LINE_4 = "YOU NEED TO BE";
export const HERO_TAGLINE = "STRUCTURED PROGRAMS · SENIOR PRACTITIONERS · SMALL COHORTS";
export const HERO_CTA_PRIMARY = "BOOK A CONSULTATION";
export const HERO_CTA_SECONDARY = "VIEW PROGRAMS";
export const HERO_VIDEO_URL = "https://videos.pexels.com/video-files/3251563/3251563-hd_1920_1080_25fps.mp4";
export const HERO_VIDEO_POSTER =
  "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?auto=format&fit=crop&w=2400&q=70";

// Stats — counter-up section
export type Stat = { value: string; label: string };
export const STATS: Stat[] = [
  { value: "500+", label: "Executives Coached" },
  { value: "12+", label: "Program Tracks" },
  { value: "5+", label: "Years Practicing" },
  { value: "100%", label: "Confidential Engagements" },
];

// Programs / Courses — the catalog clients enroll in (CRITICAL section per DNA)
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
    id: "foundations",
    name: "Leadership Foundations",
    description:
      "The entry program for new managers and rising leaders. Communication fundamentals, feedback frameworks, and the language you need to lead a team with confidence.",
    level: "Beginner",
    duration: "6 weeks",
  },
  {
    id: "strategic-communication",
    name: "Strategic Communication",
    description:
      "Build influence beyond your title. Stakeholder mapping, executive narrative, and structured persuasion for leaders who present to senior audiences.",
    level: "Intermediate",
    duration: "8 weeks",
  },
  {
    id: "executive-presence",
    name: "Executive Presence",
    description:
      "Refine the way you show up in the room. Voice, posture, decision-making under scrutiny, and the executive habits that earn trust at the senior level.",
    level: "Advanced",
    duration: "10 weeks",
    featured: true,
  },
  {
    id: "private-coaching",
    name: "Private 1:1 Coaching",
    description:
      "One coach, one executive, confidential engagement. Custom development plan built around your specific role, transition, or strategic challenge.",
    level: "All Levels",
    duration: "90 minutes",
    featured: true,
  },
  {
    id: "leadership-under-pressure",
    name: "Leadership Under Pressure",
    description:
      "Decision-making, communication, and composure in high-stakes moments. Designed for executives navigating reorganizations, crisis response, or board scrutiny.",
    level: "Advanced",
    duration: "6 weeks",
  },
  {
    id: "team-strategy-clinic",
    name: "Team Strategy Clinic",
    description:
      "A focused two-session clinic for senior leaders and their direct teams. Align on priorities, surface friction, and leave with a clear quarterly operating plan.",
    level: "All Levels",
    duration: "2 sessions",
  },
];

// Coach bio (authority signal — major DNA element)
export const INSTRUCTOR_NAME = "[COACH NAME]";
export const INSTRUCTOR_TITLE = "Founder & Principal Coach";
export const INSTRUCTOR_IMAGE_URL =
  "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=1200&q=70";
export const INSTRUCTOR_BIO = [
  "I founded Veridian Executive Coaching because I wanted a practice where senior leaders get the depth of partnership they actually need — no frameworks for the sake of frameworks, no theater, just structured work that builds judgment.",
  "Every engagement I run is the same way I'd advise a peer. Confidential conversations, honest feedback, and a development plan that earns its name.",
];
export const INSTRUCTOR_CREDENTIALS = [
  "Credentialed executive coach with documented coaching hours",
  "Continuing education in leadership and organizational practice",
  "Confidentiality agreements and engagement contracts in writing",
  "References available on request from prior clients",
];

// Mission / philosophy blockquote
export const MISSION_EYEBROW = "Our Practice";
export const MISSION_QUOTE =
  "We don't sell certificates. We build judgment — the kind that holds up when the stakes are real. Clarity. Strategy. Results.";
export const MISSION_BODY =
  "Every Veridian engagement is built around measurable change and a clear path to the next chapter of your leadership. That's the bar. If a program doesn't meet it, we redesign it.";

// Offer / discount banner — flexible CTA section
export const OFFER_HEADING = "First-Time Client Consultation";
export const OFFER_BODY =
  "New to executive coaching? Your first consultation is complimentary when you book within 30 days of your initial inquiry. Mention the offer below.";
export const OFFER_CTA = "Claim the Consultation";

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
export const PHONE_DISPLAY = "(212) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS], New York, NY";
export const HOURS = "Mon–Fri 9AM–6PM · Evening sessions by appointment";
export const SERVICE_AREAS = ["New York City", "Tri-State Area"];

// Footer
export const FOOTER_TAGLINE = "Clarity. Strategy. Results.";
export const FOOTER_NAV = [
  { label: "Home", href: "/" },
  { label: "Programs", href: "/courses" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Navigation
export const NAV_LINKS = [
  { label: "Programs", href: "/courses" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

// Social links — empty strings are hidden by the Footer
export const SOCIAL = {
  instagram: "",
  facebook: "",
  youtube: "",
};
