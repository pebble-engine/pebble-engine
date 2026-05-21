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
 * Brand placeholder: "Stratford Tactical Academy" — a generic professional
 * instructor brand designed to work for firearms training, martial arts schools,
 * fitness coaching, executive coaching, or security training without rewriting
 * any component logic.
 */

export const SITE_TITLE = "Stratford Tactical Academy";
export const SITE_DESCRIPTION =
  "Professional skills training with structured curriculum, certified instructors, and serious results.";
export const TAGLINE = "Train Smart. Train Hard. Train Right.";

// Hero copy — DNA notes: 4 lines, middle line uses gold-gradient text fill
export const HERO_EYEBROW = "EST. 2019 — CERTIFIED INSTRUCTOR";
export const HERO_HEADLINE_LINE_1 = "BUILD";
export const HERO_HEADLINE_LINE_2 = "REAL";
export const HERO_HEADLINE_LINE_3_GOLD = "CONFIDENCE";
export const HERO_HEADLINE_LINE_4 = "THROUGH TRAINING";
export const HERO_TAGLINE = "STRUCTURED CURRICULUM · CERTIFIED INSTRUCTOR · SMALL GROUPS";
export const HERO_CTA_PRIMARY = "ENROLL NOW";
export const HERO_CTA_SECONDARY = "VIEW COURSES";
export const HERO_VIDEO_URL = "https://videos.pexels.com/video-files/4761711/4761711-hd_1920_1080_25fps.mp4";
export const HERO_VIDEO_POSTER =
  "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?auto=format&fit=crop&w=2400&q=70";

// Stats — counter-up section
export type Stat = { value: string; label: string };
export const STATS: Stat[] = [
  { value: "500+", label: "Students Trained" },
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
    id: "foundations",
    name: "Foundations Course",
    description:
      "The entry-level curriculum. Stance, fundamentals, safety, and the language you need to progress to every other class in the academy.",
    level: "Beginner",
    duration: "4 hours",
  },
  {
    id: "intermediate-skills",
    name: "Intermediate Skills",
    description:
      "Build on the Foundations. Drills, movement under pressure, and decision-making at speed. Required prerequisite: Foundations or instructor approval.",
    level: "Intermediate",
    duration: "6 hours",
  },
  {
    id: "advanced-practical",
    name: "Advanced Practical",
    description:
      "Scenario-based work for students with documented experience. Real-world problem solving, structured stress, and performance feedback.",
    level: "Advanced",
    duration: "8 hours",
    featured: true,
  },
  {
    id: "private-coaching",
    name: "Private 1:1 Coaching",
    description:
      "One instructor, one student, full session. Custom curriculum built around your specific goals and timeline.",
    level: "All Levels",
    duration: "2 hours",
    featured: true,
  },
  {
    id: "group-fundamentals",
    name: "Group Fundamentals",
    description:
      "A small-group format (4-6 students) covering the core curriculum in a cohort. Bring a friend, train together, learn faster.",
    level: "Beginner",
    duration: "4 hours",
  },
  {
    id: "refresher-clinic",
    name: "Refresher Clinic",
    description:
      "A focused 2-hour clinic for returning students. Re-set fundamentals, address sticky points, leave with a personal practice plan.",
    level: "All Levels",
    duration: "2 hours",
  },
];

// Instructor bio (authority signal — major DNA element)
export const INSTRUCTOR_NAME = "[INSTRUCTOR NAME]";
export const INSTRUCTOR_TITLE = "Founder & Lead Instructor";
export const INSTRUCTOR_IMAGE_URL =
  "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=1200&q=70";
export const INSTRUCTOR_BIO = [
  "I started Stratford Tactical Academy because I wanted a place where students learn the right way the first time — no shortcuts, no theatrics, just structured instruction that builds real competence.",
  "Every course I run is the same way I'd teach a family member. Small groups, honest feedback, and a curriculum that earns its name.",
];
export const INSTRUCTOR_CREDENTIALS = [
  "Certified instructor with documented training hours",
  "Continuing education updated annually",
  "Insured and licensed for instruction in this jurisdiction",
  "Background-checked and references available on request",
];

// Mission / philosophy blockquote
export const MISSION_EYEBROW = "Our Mission";
export const MISSION_QUOTE =
  "We don't sell certificates. We build competence — the kind that holds up when it matters. Train smart. Train hard. Train right.";
export const MISSION_BODY =
  "Every Stratford Tactical Academy student walks out of class with measurable improvement and a clear path to the next level. That's the bar. If a class doesn't meet it, we redesign it.";

// Offer / discount banner — flexible CTA section
export const OFFER_HEADING = "First-Time Student Discount";
export const OFFER_BODY =
  "New to the academy? Your first Foundations Course is 20% off when you enroll within 30 days of your first contact. Mention the offer below.";
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
export const PHONE_DISPLAY = "(203) 555-0142";
export const EMAIL = "[BUSINESS EMAIL]";
export const ADDRESS = "[BUSINESS ADDRESS], Stratford, CT";
export const HOURS = "Tue–Fri 10AM–8PM · Sat 8AM–4PM · Sun by appointment";
export const SERVICE_AREAS = ["Fairfield County", "New Haven County"];

// Footer
export const FOOTER_TAGLINE = "Train smart. Train hard. Train right.";
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
