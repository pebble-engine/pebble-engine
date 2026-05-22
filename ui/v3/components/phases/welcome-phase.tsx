"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence, MotionConfig, useScroll, useTransform } from "framer-motion";
import { ArrowRight, Sparkles, Palette, Rocket, Check, AlertCircle } from "lucide-react";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
import { BackgroundCarousel } from "@/components/hero/background-carousel"; // eslint-disable-line @typescript-eslint/no-unused-vars -- kept for quick revert
import { ShuffleHeroBackdrop } from "@/components/hero/shuffle-grid";
import { LandingNav } from "@/components/hero/landing-nav";
import { DetectiveInput } from "@/components/hero/detective-input";
import { SwiperSteps, type SwiperStep } from "@/components/hero/swiper-steps"; // eslint-disable-line @typescript-eslint/no-unused-vars -- kept for quick revert
import { BuildDemo } from "@/components/hero/build-demo";
import { TakeoffMoment } from "@/components/hero/takeoff-moment";
import { MarqueeShowcase } from "@/components/hero/marquee-showcase";
import {
  patchBrief,
  getUserProfile,
  getLastBuild,
  getBrief,
  deriveProjectName,
} from "@/lib/state";
import { SHORT_S, EASE_CINEMATIC, withReducedMotion } from "@/lib/motion";
import { type } from "@/lib/type";
import { cn } from "@/lib/utils";
import { useAuth } from "@/components/auth-provider";
import {
  createCheckoutSession,
  fetchSubscription,
  extractBrand,
  fetchSmartDefaults,
  type SubscriptionState,
  type BrandExtractResult,
  type ExtractMode,
  type MatchedDNA,
} from "@/lib/api";

/**
 * URL-detection regex for Phase 33c. Tight on purpose — we treat
 * something as a URL only if it parses cleanly as one with no spaces.
 * False negatives are fine ("acme dot co" → free text). False positives
 * would route plain text through the extractor and waste a request.
 */
const URL_LIKE_RX = /^(https?:\/\/)?[a-z0-9-]+(\.[a-z0-9-]+)+(\/\S*)?$/i;

function looksLikeUrl(input: string): boolean {
  const trimmed = input.trim();
  if (!trimmed || trimmed.length > 200) return false;
  if (/\s/.test(trimmed)) return false;
  return URL_LIKE_RX.test(trimmed);
}

/**
 * Welcome / landing page.
 *
 * Full-bleed dark scrolling surface. Simple hero (no scroll morph) + a
 * stack of marketing sections below that fade in as they enter view.
 *
 *   §1 Hero          welcome to Pebble. / Let's build your [carousel] / CTA
 *   §2 Meet Pebble   3-step explainer
 *   §3 DNA showcase  8 real Style DNA personalities
 *   §4 Perfect for…  business types we route well
 *   §5 Testimonial   honest blank for first beta user
 *   §6 Pricing tease 3 tiers → /pricing
 *   §7 Ready to build? final CTA with chat input
 *   §8 Footer
 *
 * Pebble wordmark stays hidden top-left until the user clicks
 * Start Building Free; then fades in as a glass pill.
 */

const ROTATING_WORDS = [
  "future",   "business", "vision",  "path",
  "legacy",   "dream",    "brand",   "story",
  "empire",   "presence", "purpose", "voice",
] as const;

/** "Pebble" translated into 8 world languages — for the rotating nav + footer wordmark. */
const PEBBLE_LANGS = [
  "Pebble",     // English
  "Guijarro",   // Español
  "Caillou",    // Français
  "Kiesel",     // Deutsch
  "Seixo",      // Português
  "小石",        // 日本語
  "자갈",        // 한국어
  "Ciottolo",   // Italiano
] as const;

const STEPS = [
  {
    Icon: Sparkles,
    title: "Start with an idea",
    body: "Describe your business in your own words. No jargon. No templates to wade through.",
  },
  {
    Icon: Palette,
    title: "Pebble builds it live",
    body: "Watch your site come together piece by piece, with every choice explained.",
  },
  {
    Icon: Rocket,
    title: "Refine and publish",
    body: "Edit anything with a click. Publish when you're ready. Change it anytime.",
  },
];

/** Phase 43 — DNA showcase visualized as palette swatches instead of
    text descriptions. Each DNA gets 4 representative colors lifted from
    its signature palette (in style_dna.py) and a `preview` PNG from the
    template gallery — at tile size, palette + name + hover-revealed
    preview do the heavy lifting. Drops the "feel" paragraph that
    nobody was reading.
    Phase 43.3 — added `preview` so on hover we reveal a real template
    PNG in that DNA. Mapping below picks the closest visual match from
    public/templates-preview/. */
const DNAS = [
  { label: "Swiss Magazine",        colors: ["#1a1a1a", "#ffffff", "#dc2626", "#f5f5f5"], feel: "Editorial · quiet authority", preview: "/templates-preview/instructor_pro.png"       },
  { label: "Cinematic IMAX",        colors: ["#0a1428", "#1e3a5f", "#c19a6b", "#f5f0e8"], feel: "Widescreen · dramatic",        preview: "/templates-preview/service_pro_navy.png"    },
  { label: "Garden Press",          colors: ["#f5f0e1", "#5b6f4a", "#8b6f47", "#2a2a1f"], feel: "Botanical · considered",       preview: "/templates-preview/artisan_kitchen.png"     },
  { label: "Velvet Lounge",         colors: ["#1a0f1f", "#722f4a", "#c4a058", "#f3e5cc"], feel: "Intimate · candlelit",         preview: "/templates-preview/ink_studio_oxblood.png"  },
  { label: "Tactile Y2K",           colors: ["#ffe4ec", "#f0e6d2", "#a8c8e8", "#3d3d3d"], feel: "Soft · organic",               preview: "/templates-preview/luxe_beauty_rose.png"    },
  { label: "Industrial Freight",    colors: ["#1f1f1f", "#f97316", "#9ca3af", "#fef3c7"], feel: "Utilitarian · blocky",         preview: "/templates-preview/honest_garage_rust.png"  },
  { label: "Marina",                colors: ["#0c2340", "#ffffff", "#c9a96e", "#a8c8d8"], feel: "Salt-air premium",             preview: "/templates-preview/boutique_brokerage_navy.png" },
  { label: "Postmodern Maximalist", colors: ["#ff006e", "#3a86ff", "#ffbe0b", "#000000"], feel: "Loud · layered",               preview: "/templates-preview/ink_studio.png"          },
] as const;

/** Phase 43 — "Perfect for" replaces text-only chips with the new
    hero-craft photos. Anchors the section emotionally: small business
    owners see themselves in the imagery, not a flat tag list. Photos
    are the same set the hero ShuffleGrid uses (one origin of truth);
    we just render 8 of them as a grid below. */
const PERFECT_FOR = [
  { label: "Coffee shops + cafés",       photo: "/hero-craft/barista.jpg"              },
  { label: "Photographers",              photo: "/hero-craft/wedding-photographer.jpg" },
  { label: "Restaurants + food trucks",  photo: "/hero-craft/chef.jpg"                 },
  { label: "Coaches + trainers",         photo: "/hero-craft/personal-trainer.jpg"     },
  { label: "Salons + beauty",            photo: "/hero-craft/hairstylist.jpg"          },
  { label: "Trades + contractors",       photo: "/hero-craft/auto-mechanic.jpg"        },
  { label: "Florists + boutiques",       photo: "/hero-craft/florist.jpg"              },
  { label: "Artists + studios",          photo: "/hero-craft/tattoo-artist.jpg"        },
];

type FeatureCategory = { category: string; items: readonly string[] };

type PricingTier = {
  name: string;
  monthly: number | null;
  yearly: number | null;
  desc: string;
  highlights: readonly string[];
  details: readonly FeatureCategory[];
  cta: string;
  ctaHref?: string;
  stripePlan?: "starter" | "pro";
  featured?: boolean;
};

const PRICING_TIERS: readonly PricingTier[] = [
  {
    name: "Free",
    monthly: 0,
    yearly: 0,
    desc: "See what Pebble can do.",
    highlights: ["1 site", "30 AI refinements/mo", "pebble.app subdomain", "Unlimited cosmetic edits"],
    details: [
      { category: "Sites & publishing", items: ["1 generated site", "Free pebble.app subdomain", "Contact form on every site"] },
      { category: "Editing",             items: ["Visual click-to-edit (unlimited)", "Color + style swaps (unlimited)", "30 AI refinements/month", "60-second undo refund"] },
      { category: "Support",             items: ["Community support"] },
    ],
    cta: "Start free",
  },
  {
    name: "Starter",
    monthly: 19,
    yearly: 190,
    desc: "For one real business.",
    highlights: ["5 sites", "150 AI refinements/mo (rollover)", "1 custom domain", "Real email forms"],
    details: [
      { category: "Sites & publishing", items: ["5 generated sites", "1 custom domain", "Real email forms (Resend-backed)"] },
      { category: "Editing",             items: ["Everything in Free", "150 AI refinements/month", "Rollover up to 300", "+100 Launch Bonus on first month"] },
      { category: "Forms & analytics",   items: ["Form submissions inbox"] },
      { category: "Support",             items: ["Email support"] },
    ],
    cta: "Start free trial",
    stripePlan: "starter",
    featured: true,
  },
  {
    name: "Pro",
    monthly: 49,
    yearly: 490,
    desc: "For agencies + serial builders.",
    highlights: ["Unlimited sites", "400 AI refinements/mo (rollover)", "5 custom domains", "Priority builds"],
    details: [
      { category: "Sites & publishing", items: ["Unlimited sites", "5 custom domains", "Multi-page sites (About, FAQ, …)", "Drop-in section library"] },
      { category: "Editing",             items: ["Everything in Starter", "400 AI refinements/month", "Rollover up to 800", "Priority generation queue"] },
      { category: "Forms & analytics",   items: ["7-day site analytics"] },
      { category: "Support",             items: ["Priority email support"] },
    ],
    cta: "Start free trial",
    stripePlan: "pro",
  },
  {
    name: "Enterprise",
    monthly: null,
    yearly: null,
    desc: "For teams + white-label.",
    highlights: ["Everything in Pro", "Unlimited domains + white-label", "Team workspace + SSO", "Dedicated support + SLA"],
    details: [
      { category: "Sites & publishing", items: ["Everything in Pro", "Unlimited custom domains", "White-label (remove Pebble branding)"] },
      { category: "Team",                items: ["Multi-seat workspace", "SSO / SAML", "Role-based access"] },
      { category: "Support",             items: ["Dedicated success manager", "Custom SLA", "Onboarding + training"] },
    ],
    cta: "Contact us",
    ctaHref: "mailto:hello@pebble.app",
  },
] as const;

type Props = {
  onAdvance: () => void;
};

const SECTION_REVEAL = {
  initial: { opacity: 0, y: 40 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.2 },
  transition: { duration: 0.7, ease: EASE_CINEMATIC },
} as const;

const darkGradient = "text-white";
const lightGradient = "text-foreground";

/* Phase 40j (2026-05-21) — NAV_ITEMS + shimmerSilverStyle removed.
   Both were only consumed by the retired TopNavBar() function. NAV_ITEMS
   now lives in components/hero/landing-nav.tsx. */

/**
 * Foreground-aware shimmer for light / dark surfaces (footer, etc.).
 * Uses CSS custom properties so it resolves to the right tones in each
 * theme — near-black on sand in light mode, near-white on #0a0a0a in dark.
 */
const shimmerForegroundStyle: React.CSSProperties = {
  backgroundImage:
    "linear-gradient(90deg, var(--color-muted-foreground) 0%, var(--color-foreground) 40%, var(--color-foreground) 60%, var(--color-muted-foreground) 100%)",
  backgroundSize: "200% auto",
};

/**
 * Cycles through PEBBLE_LANGS with a shimmering gradient clipped to the
 * text. Usable on both dark (nav) and light (footer) surfaces — just
 * pass the appropriate shimmerStyle.
 */
function RotatingPebbleLogo({
  shimmerStyle,
  className = "",
}: {
  shimmerStyle: React.CSSProperties;
  className?: string;
}) {
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % PEBBLE_LANGS.length), 2800);
    return () => clearInterval(id);
  }, []);

  return (
    <MotionConfig reducedMotion="never">
      {/* aria-label="Pebble" so screen readers always hear the brand name */}
      <span aria-label="Pebble" className={`relative inline-block font-logo tracking-[0.12em] ${className}`}>
        {/* invisible max-width anchor — "Guijarro" is the longest word */}
        <span aria-hidden className="invisible select-none">Guijarro</span>
        <AnimatePresence mode="wait">
          <motion.span
            key={PEBBLE_LANGS[idx]}
            initial={{ opacity: 0, y: 6 }}
            animate={{
              opacity: 1,
              y: 0,
              backgroundPosition: ["0% 0%", "200% 0%"],
            }}
            exit={{ opacity: 0, y: -6 }}
            transition={{
              opacity: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
              y:       { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
              backgroundPosition: { duration: 3.5, repeat: Infinity, ease: "linear" },
            }}
            className="absolute left-0 top-0 bg-clip-text text-transparent whitespace-nowrap"
            style={shimmerStyle}
          >
            {PEBBLE_LANGS[idx]}
          </motion.span>
        </AnimatePresence>
      </span>
    </MotionConfig>
  );
}

/**
 * Phase 40j (2026-05-21) — TopNavBar() retired. Replaced by `LandingNav`
 * (header-2 pattern: sticky pill that shrinks on scroll + mobile menu
 * + Sign In / Get Started CTAs). See components/hero/landing-nav.tsx.
 * NAV_ITEMS now lives only in landing-nav; the shimmerForegroundStyle +
 * RotatingPebbleLogo remain used by the footer below.
 */

/* ---------------------------------------------------------------------------
 * Phase 43.4 (2026-05-21) — CountUp + plan-picker quiz helpers.
 *
 * CountUp: tiny rAF-driven number ticker. Eases from 0 → target over
 * `durationMs` when `run` flips to true. Pricing tier cards use it to
 * count up the dollar amount on first scroll-into-view — satisfying
 * dopamine moment that costs almost nothing.
 *
 * PlanPickerQuiz: 2-question micro-quiz ("How many sites?" + "Custom
 * domain?"). Maps the answers to a recommended Pebble tier; the
 * recommendation pulses the matching card via the same ledTier
 * mechanism the click-LED uses. Genuinely useful, not just decorative.
 * --------------------------------------------------------------------------- */

function useCountUp(target: number, durationMs: number, run: boolean): number {
  const [val, setVal] = useState(0);
  useEffect(() => {
    if (!run) { setVal(0); return; }
    let raf = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const elapsed = now - start;
      const t = Math.min(1, elapsed / durationMs);
      const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      setVal(Math.round(target * eased));
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, durationMs, run]);
  return val;
}

type QuizSites  = "one" | "few" | "many";
type QuizDomain = "no"  | "yes";

/** Returns the recommended tier name from the answer pair. Mirrors the
    real tier mechanics: Free covers 1 site no domain, Starter covers
    1-5 sites + a custom domain, Pro covers unlimited. */
function recommendTier(sites: QuizSites | null, domain: QuizDomain | null): string | null {
  if (sites === null || domain === null) return null;
  if (sites === "many")               return "Pro";
  if (sites === "few")                return "Starter";
  return domain === "yes" ? "Starter" : "Free";
}

/**
 * Phase 43 (2026-05-21) — mobile-detect hook. Used to skip the sticky-
 * scroll + scroll-tied parallax on §3–§7 on iPhone-sized screens, where
 * 1000+vh of scroll-jacked sections was murdering Marc's navigation
 * experience. On md+ the cinematic pinning stays exactly as Phase 40g
 * shipped it; on mobile each section becomes a simple stacked panel
 * with a one-shot fade-in via whileInView. SSR-safe (returns false until
 * the first client-side measurement).
 */
function useIsMobile(maxWidthPx = 768): boolean {
  const [isMobile, setIsMobile] = useState(false);
  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia(`(max-width: ${maxWidthPx}px)`);
    const apply = () => setIsMobile(mq.matches);
    apply();
    mq.addEventListener("change", apply);
    return () => mq.removeEventListener("change", apply);
  }, [maxWidthPx]);
  return isMobile;
}

/**
 * Mobile fade-in motion props — applied to section content via spread
 * when isMobile is true. Replaces the desktop scroll-tied transforms
 * with a single one-shot animation when the element enters the viewport.
 */
const MOBILE_FADE_PROPS = {
  initial:    { opacity: 0, y: 16 },
  whileInView:{ opacity: 1, y: 0 },
  viewport:   { once: true, amount: 0.2 },
  transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] as const },
};

/**
 * Sticky-pinned section. Phase 40g (2026-05-21) — Marc's call: §3–§7
 * (DNA showcase → Perfect for → testimonial → pricing → final CTA) all
 * use the same pinned-stage pattern. Each section is tall (configurable
 * via `vh`) and contains a `sticky top-0 h-screen` inner. As the user
 * scrolls into the section, content reveals via scroll-tied transforms;
 * the inner pins for the middle ~half of the section's scroll range,
 * then unpins to the next section's pin. Feels like a guided tour
 * where each marketing beat gets its own viewport moment.
 *
 * Offset is `["start start", "end end"]` so scrollYProgress maps cleanly
 * to the pin lifecycle: 0 = section top hits viewport top (pin starts),
 * 1 = section bottom hits viewport bottom (pin releases).
 *
 * Reveal curve:
 *   - 0 → 0.25: enter (content rises + scales up + fades in)
 *   - 0.25 → 0.75: dwell at full opacity, neutral position
 *   - 0.75 → 1: exit (content lifts + scales down + fades out)
 */
function useStickySection() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end end"],
  });
  return {
    ref,
    scrollYProgress,
    headingY: useTransform(scrollYProgress, [0, 0.25, 0.75, 1], [80, 0, 0, -60]),
    bodyY:    useTransform(scrollYProgress, [0, 0.25, 0.75, 1], [120, 0, 0, -40]),
    scale:    useTransform(scrollYProgress, [0, 0.25, 0.75, 1], [0.9, 1, 1, 0.94]),
    opacity:  useTransform(scrollYProgress, [0, 0.15, 0.85, 1], [0, 1, 1, 0]),
  };
}

/** Stagger-children variants used by every grid/list in §3-§6.
    Items rise 32px + fade in on scroll-into-view; container drives the
    timing so cards / chips / tiers cascade in instead of popping all
    at once. */
/* Raw variants — wrap with withReducedMotion() at the consumption site
   (see WelcomePhase below). The wiring test (test_motion_module_wiring)
   enforces this: if a component imports named variants, it must pass
   them through withReducedMotion() so the OS reduce-motion preference
   collapses them to instant transitions. */
const STAGGER_PARENT_RAW = {
  hidden: {},
  show: {
    transition: {
      staggerChildren: 0.08,
      delayChildren:   0.1,
    },
  },
};
const STAGGER_CHILD_RAW = {
  hidden: { opacity: 0, y: 32, scale: 0.96 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] as const },
  },
};

export function WelcomePhase({ onAdvance }: Props) {
  const router = useRouter();
  const [firstName, setFirstName] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [wordIdx, setWordIdx] = useState(0);
  const [started, setStarted] = useState(false);
  const [billing, setBilling] = useState<"monthly" | "yearly">("monthly");
  const [expandedTiers, setExpandedTiers] = useState<Set<string>>(new Set());
  // Phase 43 — track the tier whose LED is currently pulsing, so we can
  // strip the className when the animation finishes (otherwise the
  // keyframe re-fires on next click only when the class is added fresh).
  const [ledTier, setLedTier] = useState<string | null>(null);

  // Phase 43.4 — plan-picker micro-quiz state. Sites + domain answers
  // map to a recommended tier; the recommendation pulses the matching
  // card (reuses ledTier). Count-up ticker for prices triggers when the
  // pricing section enters view (pricingInView).
  const [quizSites,  setQuizSites]  = useState<QuizSites  | null>(null);
  const [quizDomain, setQuizDomain] = useState<QuizDomain | null>(null);
  const [pricingInView, setPricingInView] = useState(false);

  // Per-tier count-up tickers. Rules of Hooks: must be called at the
  // top of the component, not inside the .map() that renders cards.
  // Targets recompute when billing toggles so the digits visibly morph
  // between monthly / yearly.
  const tickStarter = useCountUp(
    billing === "monthly" ? 19 : Math.round(190 / 12),
    900,
    pricingInView,
  );
  const tickPro = useCountUp(
    billing === "monthly" ? 49 : Math.round(490 / 12),
    900,
    pricingInView,
  );
  const priceTickers: Record<string, number> = {
    Free:       0,
    Starter:    tickStarter,
    Pro:        tickPro,
    Enterprise: 0,
  };
  const recommendedTier = recommendTier(quizSites, quizDomain);
  // Pulse the recommended tier whenever the recommendation lands or
  // changes. Same 1.4s LED animation as the manual click.
  useEffect(() => {
    if (!recommendedTier) return;
    setLedTier(null);
    const raf = requestAnimationFrame(() => {
      setLedTier(recommendedTier);
      window.setTimeout(() => setLedTier((cur) => (cur === recommendedTier ? null : cur)), 1400);
    });
    return () => cancelAnimationFrame(raf);
  }, [recommendedTier]);
  const [stripeLoading, setStripeLoading] = useState<string | null>(null);
  const [stripeError, setStripeError] = useState<string | null>(null);
  const [stripeErrorTierId, setStripeErrorTierId] = useState<string | null>(null);
  const [sub, setSub] = useState<SubscriptionState | null | "loading">("loading");
  const { user } = useAuth();

  useEffect(() => {
    if (!user) { setSub(null); return; }
    fetchSubscription().then(setSub).catch(() => setSub(null));
  }, [user]);

  const toggleTier = (name: string) => {
    setExpandedTiers((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
    // Phase 43 — fire the LED pulse. Re-trigger by clearing the class
    // first (in case the user clicks twice in quick succession) and
    // then re-applying on the next tick.
    setLedTier(null);
    requestAnimationFrame(() => {
      setLedTier(name);
      window.setTimeout(() => setLedTier((cur) => (cur === name ? null : cur)), 1400);
    });
  };

  const activePlan = (sub && sub !== "loading" && sub.status === "active") ? sub.plan : null;

  const handleChoosePlan = async (tier: PricingTier) => {
    // Free / no Stripe → open the questionnaire flow inline.
    if (!tier.stripePlan) {
      handleStartClick();
      return;
    }
    // Logged out → bounce to signup, then back to the landing pricing anchor.
    if (!user) {
      router.push(`/signup?redirect=${encodeURIComponent("/#pricing")}`);
      return;
    }
    // Already subscribed → manage in settings instead of double-charging.
    if (activePlan) {
      router.push("/settings");
      return;
    }
    setStripeLoading(tier.name);
    setStripeError(null);
    setStripeErrorTierId(null);
    try {
      const { url } = await createCheckoutSession(tier.stripePlan);
      window.location.href = url;
    } catch (err) {
      setStripeError(err instanceof Error ? err.message : "Something went wrong. Try again.");
      setStripeErrorTierId(tier.name);
      setStripeLoading(null);
    }
  };

  // Parallax — document-scroll tied transforms. Blobs move slower than
  // scroll (depth), hero text lifts gently as you leave the hero behind.
  const { scrollY } = useScroll();
  // Phase 40c (2026-05-21) — third pass on hero/scroll motion. Marc
  // clarified: he WANTS the cinematic parallax moment at the hero →
  // section-2 boundary. The earlier "broken parallax" report was about
  // the boundary feeling FLAT, not about jank. So we restore a subtle
  // "hero recedes" effect (scale 1 → 0.97 + opacity 1 → 0.6) tied to
  // scroll progress over the first 600px. The §2 section then enters
  // with weight (see whileInView animations on its heading + cards).
  // Blobs stay anchored — competing y-transforms over the carousel
  // were the actual jank source.
  const blobYTop      = useTransform(scrollY, [0, 1000], [0, 0]);
  const blobYBottom   = useTransform(scrollY, [0, 1000], [0, 0]);
  const heroLift      = useTransform(scrollY, [0, 600], [0, -24]);     // gentle recede
  const heroFadeOut   = useTransform(scrollY, [100, 600], [1, 0.6]);   // recede + fade
  const heroScale     = useTransform(scrollY, [0, 600], [1, 0.97]);    // backwards-scale cue

  // One parallax setup per marketing section.
  // (sentenceSec removed in Phase 40e — §2 now uses StickyScrollStack
  // which manages its own scroll progress. Leaving the orphan hook here
  // throws "Target ref is defined but not hydrated" because the ref
  // never gets attached to any element.)
  const dnaSec      = useStickySection();
  const perfectSec  = useStickySection();
  const quoteSec    = useStickySection();
  const pricingSec  = useStickySection();
  const ctaSec      = useStickySection();

  // Phase 43 — read once per render; gates the sticky-pin + scroll-tied
  // parallax on §3-§7. On mobile we render stacked panels with fade-in;
  // on md+ the cinematic pinning stays in.
  const isMobile = useIsMobile();

  useEffect(() => {
    if (typeof window === "undefined") return;
    const id = window.setInterval(() => {
      setWordIdx((i) => (i + 1) % ROTATING_WORDS.length);
    }, 2200);
    return () => window.clearInterval(id);
  }, []);

  useEffect(() => {
    const profile = getUserProfile();
    setFirstName(profile.firstName || null);
    const build = getLastBuild();
    if (build?.slug) {
      const brief = getBrief();
      const name = (brief.business_name as string) || "your last project";
      setResumeName(name);
    }
    setMounted(true);
  }, []);

  const handleResume = () => {
    router.push("/workspace#phase=design");
  };

  const handleStartClick = () => {
    setStarted(true);
  };

  // Phase 33c/d — URL ingestion state.
  const [extracting, setExtracting] = useState(false);
  const [extractStepIdx, setExtractStepIdx] = useState(0);
  const [extractError, setExtractError] = useState<string | null>(null);

  // Phase 34 (2026-05-21) — Build intent (Business default; Project opt-in
  // for devs/designers). Stamped onto brief.intent before advance.
  const [buildIntent, setBuildIntent] = useState<"business" | "project">("business");

  // Phase 33d — Mode picker state.
  // When a URL is detected, show the intent picker before extraction fires.
  const [awaitingModeChoice, setAwaitingModeChoice] = useState(false);
  const [pendingUrl, setPendingUrl] = useState<string>("");
  const [pendingFiles, setPendingFiles] = useState<File[] | undefined>(undefined);
  const [extractMode, setExtractMode] = useState<ExtractMode>("brand");
  const [matchedDnaResult, setMatchedDnaResult] = useState<MatchedDNA | null>(null);
  const [inspireResult, setInspireResult] = useState<BrandExtractResult | null>(null);

  const BRAND_STEPS = [
    "Reading your site…",
    "Detecting your brand palette…",
    "Identifying your industry…",
    "Got it — let's go.",
  ];

  const INSPIRE_STEPS = [
    "Reading the reference site…",
    "Capturing the visual vibe…",
    "Matching to a Pebble design system…",
    "Got it — we'll build something inspired by this.",
  ];

  const EXTRACT_STEPS = extractMode === "inspire" ? INSPIRE_STEPS : BRAND_STEPS;

  // Phase 40g sticky-scroll stagger variants — wrapped via withReducedMotion
  // so OS reduce-motion flattens them to instant transitions. Memoized so
  // we don't re-wrap on every render. Required by tests/test_motion_module_wiring.
  const STAGGER_PARENT = useMemo(() => withReducedMotion(STAGGER_PARENT_RAW), []);
  const STAGGER_CHILD  = useMemo(() => withReducedMotion(STAGGER_CHILD_RAW),  []);

  // Phase 33d (fixed 2026-05-21) — Cycle narration WHILE the request is in
  // flight. The auto-cycle caps at the SECOND-TO-LAST step (e.g. "Matching
  // to a Pebble design system…") so we never declare "Got it" before the
  // actual response arrives. runExtraction() jumps to the final step
  // ("Got it — let's go.") right before applyExtractionAndAdvance runs.
  // Previously this was capped at LAST step → users saw "Got it" for 30+s
  // while Qwen Plus was still inferring style + matching DNA.
  useEffect(() => {
    if (!extracting) {
      setExtractStepIdx(0);
      return;
    }
    // Cap at LENGTH-2: the last step is reserved for "I have the answer now."
    const lastNarrationIdx = Math.max(0, EXTRACT_STEPS.length - 2);
    const id = window.setInterval(() => {
      setExtractStepIdx((i) => Math.min(i + 1, lastNarrationIdx));
    }, 900);
    return () => window.clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [extracting, extractMode]);

  /**
   * Apply a successful extraction result to the brief and advance.
   *
   * Brand mode field mapping:
   *   business_name → brief.business_name
   *   industry       → brief.business_type   (snake_case slot the engine uses)
   *   tone           → brief.brand_tone
   *   palette        → brief._brand_palette  (derived; engine consumes optionally)
   *   logo_url       → brief._extracted_logo_url
   *   favicon_url    → brief._extracted_favicon_url
   *   hero_copy      → brief._extracted_hero_copy
   *   tagline        → brief._extracted_tagline
   *   _inspired_by   → brief._inspired_by    (mirrors the /api/inspire convention)
   *
   * Inspire mode additionally patches:
   *   _design_dna_id       → matched_dna.id  (overrides random DNA pick at build time)
   *   _inspire_source_url  → res.url
   *   Does NOT set business_name/business_type/industry — the inspire URL is
   *   just a style reference, not the user's own business.
   *
   * Also synthesizes a natural-language extra_context blob so any prompt
   * path that doesn't yet read the new fields still gets the signal.
   */
  const applyExtractionAndAdvance = async (
    sourceUrl: string,
    res: BrandExtractResult,
    files?: File[],
    mode: ExtractMode = "brand",
  ) => {
    if (mode === "inspire") {
      // Inspire: patch style-only fields; leave business identity blank.
      const blurbParts: string[] = [];
      if (res.vibe_keywords?.length) blurbParts.push(`Visual vibe: ${res.vibe_keywords.join(", ")}.`);
      if (res.font_hints?.length)    blurbParts.push(`Font direction: ${res.font_hints.join(", ")}.`);
      if (res.matched_dna)           blurbParts.push(`Inspired by ${res.matched_dna.label} design language.`);
      blurbParts.push(`(Style reference: ${sourceUrl}.)`);

      patchBrief({
        business_name:    deriveProjectName(sourceUrl),
        extra_context:    blurbParts.join(" "),
        user_first_name:  firstName || undefined,
        _design_dna_id:   res.matched_dna?.id || undefined,
        _inspire_source_url: sourceUrl,
        _brand_palette:   res.palette,
      });

      // Silently enrich with smart defaults — fire with a 3s race timeout.
      // On inspire mode we have no direct industry signal, so pass what we have.
      try {
        const defaults = await Promise.race([
          fetchSmartDefaults({ business_type: res.industry || undefined }),
          new Promise<never>((_, reject) => setTimeout(() => reject(new Error("timeout")), 8000)),
        ]);
        patchBrief({
          audience:       defaults.audience,
          site_functions: defaults.site_functions,
          brand_tone:     defaults.brand_tone,
        });
      } catch {
        // Timeout or network failure — continue without smart defaults.
      }
    } else {
      // Brand: full business identity extraction (existing behavior).
      const blurbParts: string[] = [];
      if (res.business_name) blurbParts.push(`Business name: ${res.business_name}.`);
      if (res.tagline)        blurbParts.push(`Tagline: ${res.tagline}`);
      if (res.industry)       blurbParts.push(`Industry: ${res.industry.replace(/_/g, " ")}.`);
      if (res.tone)           blurbParts.push(`Tone: ${res.tone}.`);
      if (res.hero_copy)      blurbParts.push(`Current hero copy: "${res.hero_copy}".`);
      if (res.palette.length) blurbParts.push(`Brand palette: ${res.palette.join(", ")}.`);
      blurbParts.push(`(Extracted from ${sourceUrl}.)`);

      patchBrief({
        business_name: res.business_name || deriveProjectName(sourceUrl),
        business_type: res.industry || undefined,
        brand_tone:    res.tone || undefined,
        extra_context: blurbParts.join(" "),
        user_first_name: firstName || undefined,
        _inspired_by:  sourceUrl,
        _brand_palette: res.palette,
        _extracted_logo_url:    res.logo_url || undefined,
        _extracted_favicon_url: res.favicon_url || undefined,
        _extracted_hero_copy:   res.hero_copy || undefined,
        _extracted_tagline:     res.tagline || undefined,
      });

      // Silently enrich with smart defaults from the inferred industry — 3s
      // race timeout. If it wins, great: the idea-phase shows the confirmation
      // card. If not, the user just sees the full 3-step questionnaire.
      if (res.industry) {
        try {
          const defaults = await Promise.race([
            fetchSmartDefaults({
              industry:      res.industry,
              business_type: res.industry,
              business_name: res.business_name || undefined,
            }),
            new Promise<never>((_, reject) => setTimeout(() => reject(new Error("timeout")), 8000)),
          ]);
          patchBrief({
            audience:       defaults.audience,
            site_functions: defaults.site_functions,
            brand_tone:     defaults.brand_tone,
          });
        } catch {
          // Timeout or network failure — continue without smart defaults.
        }
      }
    }

    if (files && files.length > 0) {
      sessionStorage.setItem(
        "pebble.pendingFiles",
        JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
      );
    }
    onAdvance();
  };

  /**
   * Kick off extraction for a URL once the user has confirmed their
   * intent (mode = "brand" | "inspire"). Called from both the mode
   * picker CTA and the auto-default timer.
   */
  const runExtraction = async (url: string, mode: ExtractMode, files?: File[]) => {
    setExtractMode(mode);
    setAwaitingModeChoice(false);
    setExtracting(true);
    setExtractError(null);
    setMatchedDnaResult(null);
    setInspireResult(null);

    try {
      const res = await extractBrand(url, mode, true, files);
      if (!res.ok) {
        setExtractError(res.error || "Couldn't read that site — using your URL as a hint instead.");
        await new Promise((r) => setTimeout(r, 1500));
        patchBrief({
          business_name: deriveProjectName(url),
          extra_context: `User provided URL ${url} but extraction failed: ${res.error || "unknown error"}.`,
          user_first_name: firstName || undefined,
          _inspired_by: url,
        });
        if (files && files.length > 0) {
          sessionStorage.setItem(
            "pebble.pendingFiles",
            JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
          );
        }
        onAdvance();
        return;
      }

      // Response is here — jump narration to the final "Got it — let's go."
      // step so the user sees a clear transition signal, then let it breathe
      // 600ms before advancing or revealing the matched DNA card.
      setExtractStepIdx(EXTRACT_STEPS.length - 1);
      await new Promise((r) => setTimeout(r, 600));

      if (mode === "inspire" && res.matched_dna) {
        // Show the matched-DNA card before advancing.
        setMatchedDnaResult(res.matched_dna);
        setInspireResult(res);
        // setExtracting stays false after the finally block; the card renders.
        return;
      }

      await applyExtractionAndAdvance(url, res, files, mode);
    } catch (err) {
      setExtractError(err instanceof Error ? err.message : "Network error — using your URL as a hint instead.");
      await new Promise((r) => setTimeout(r, 1500));
      patchBrief({
        business_name: deriveProjectName(url),
        extra_context: `User provided URL ${url} (extraction unavailable).`,
        user_first_name: firstName || undefined,
        _inspired_by: url,
      });
      onAdvance();
    } finally {
      setExtracting(false);
    }
  };

  const handleSend = async (message: string, files?: File[]) => {
    if (typeof window === "undefined") return;

    // Phase 34 (2026-05-21) — stamp the build intent once, BEFORE any branch.
    // Every downstream patchBrief in this function leaves it intact. The
    // engine reads brief.intent in _build_intent_block — business is the
    // default; project is opt-in via the toggle below the prompt input.
    patchBrief({ intent: buildIntent });

    // Phase 33c/d — URL fast-path. If the input looks like a URL, show
    // the mode picker (brand vs inspire) before firing extraction.
    const trimmed = message.trim();
    if (looksLikeUrl(trimmed)) {
      setPendingUrl(trimmed);
      setPendingFiles(files);
      setAwaitingModeChoice(true);
      setStarted(true);
      return;
    }

    // Free-text path (existing behavior).
    // 2026-05-20 Phase 15a: derive a real business_name from the first
    // sentence of the idea text instead of hardcoding "Untitled Project".
    const derivedName = deriveProjectName(message);
    patchBrief({
      extra_context: message,
      business_name: derivedName,
      user_first_name: firstName || undefined,
    });
    if (files && files.length > 0) {
      sessionStorage.setItem(
        "pebble.pendingFiles",
        JSON.stringify(files.map((f) => ({ name: f.name, type: f.type, size: f.size }))),
      );
    }
    onAdvance();
  };

  return (
    /* Phase 40 (2026-05-21) — light-mode-landing scope forces light tokens
       even when the user has dark mode set globally. Workspace stays dark;
       only marketing surfaces use this scope. */
    <div className="light-mode-landing relative w-full font-[family-name:var(--font-plus-jakarta-sans)] bg-background text-foreground">
      {/* Phase 40j (2026-05-21) — LandingNav replaces the old fixed-pill
          TopNavBar. Sticky pill that shrinks + gains backdrop blur on
          scroll, with Sign In + Get Started CTAs and a mobile menu.
          The old TopNavBar function (~line 295) is now dead code; left
          in place for one cycle in case we want to revert. */}
      <LandingNav />

      {/* ════════════════════════════════════════════════════════════════
          LIGHT HERO (cream/sand background, charcoal text)
          ════════════════════════════════════════════════════════════════ */}
      <section className="relative bg-background text-foreground overflow-hidden">
        {/* Phase 40j — ShuffleGrid replaces the ken-burns BackgroundCarousel.
            4×4 grid of real Pebble template PNGs reshuffles every 3s →
            constant motion reads as "Pebble builds many different
            things." Cream gradient overlay below still tunes legibility
            for the hero text on top. BackgroundCarousel kept as a file
            (not deleted) in case we want it back. */}
        <ShuffleHeroBackdrop />
        {/* Cream gradient overlay — tames the busy 4×4 shuffle behind text.
            Same dual-gradient pattern the old BackgroundCarousel used
            internally; lifted up to welcome-phase so legibility tuning
            lives next to the text it's protecting. */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background/85 via-background/65 to-background/95"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-gradient-to-r from-background/35 via-transparent to-background/35"
        />
        {/* Decorative blobs — softer pastel pulse over the grid + bg */}
        <motion.div
          aria-hidden
          style={{ y: blobYTop }}
          className="pointer-events-none absolute -top-[10%] left-[20%] w-[600px] h-[600px] bg-[#f5d5b8]/40 blur-[120px] will-change-transform"
        />
        <motion.div
          aria-hidden
          style={{ y: blobYBottom }}
          className="pointer-events-none absolute bottom-0 right-[15%] w-[500px] h-[500px] bg-[#c8d4e8]/50 blur-[120px] will-change-transform"
        />

        <motion.div
          style={{ y: heroLift, opacity: heroFadeOut, scale: heroScale }}
          className="relative z-10 min-h-screen-safe flex flex-col items-center justify-center text-center px-4 max-w-5xl mx-auto py-20 space-y-10 will-change-transform"
        >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-baseline justify-center gap-2"
        >
          <span className="text-muted-foreground text-lg sm:text-xl">welcome to</span>
          <span className="text-2xl sm:text-3xl font-semibold text-foreground">Pebble.</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6, ease: EASE_CINEMATIC }}
          className="font-semibold text-5xl sm:text-7xl lg:text-[96px] leading-[0.95] tracking-tighter text-foreground"
        >
          Let&apos;s build your{" "}
          <MotionConfig reducedMotion="never">
            <span className="relative inline-block align-baseline">
              {/* "presence" is the widest word — sets the reserved slot width */}
              <span aria-hidden className="invisible">presence</span>
              <AnimatePresence mode="wait">
                <motion.span
                  key={ROTATING_WORDS[wordIdx]}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    backgroundPosition: ["0% 0%", "200% 0%"],
                  }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{
                    opacity: { duration: 0.5, ease: EASE_CINEMATIC },
                    y:       { duration: 0.5, ease: EASE_CINEMATIC },
                    backgroundPosition: { duration: 3, repeat: Infinity, ease: "linear" },
                  }}
                  className="absolute left-0 right-0 top-0 text-center bg-clip-text text-transparent"
                  style={shimmerForegroundStyle}
                >
                  {ROTATING_WORDS[wordIdx]}
                </motion.span>
              </AnimatePresence>
            </span>
          </MotionConfig>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.75 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="text-lg sm:text-xl leading-[1.65] text-foreground max-w-xl"
        >
          One click can change everything.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.5 }}
          className="w-full max-w-2xl min-h-[64px] flex items-center justify-center"
        >
          <AnimatePresence mode="wait" initial={false}>
            {!started ? (
              /* Phase 40 (2026-05-21) — bigger CTA + light-mode treatment.
                 Charcoal pill with white text + accent arrow circle on a
                 cream background pops better than white-on-white. Slow
                 breathing shadow draws the eye without flashing. */
              <motion.div
                key="cta"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, ease: EASE_CINEMATIC }}
                className="flex flex-col items-center gap-3"
              >
                <motion.button
                  onClick={handleStartClick}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.97 }}
                  animate={{
                    boxShadow: [
                      "0 8px 28px rgba(31,29,26,0.10)",
                      "0 12px 40px rgba(48,84,255,0.20)",
                      "0 8px 28px rgba(31,29,26,0.10)",
                    ],
                  }}
                  transition={{
                    boxShadow: { duration: 3.6, repeat: Infinity, ease: "easeInOut" },
                    scale:     { duration: 0.18, ease: EASE_CINEMATIC },
                  }}
                  // Phase 43 (2026-05-21) — was uniformly huge across all
                  // viewports (text-2xl + w-14 arrow). On iPhone that read
                  // as a comically oversized banner. Now responsive: tighter
                  // on mobile, retains the cinematic feel on desktop.
                  className="group flex items-center gap-2 sm:gap-4 pl-5 sm:pl-10 pr-2 sm:pr-3 py-1.5 sm:py-3 bg-foreground rounded-full"
                >
                  <span className="font-semibold text-base sm:text-2xl text-background">Start Building Free</span>
                  <span className="w-10 h-10 sm:w-14 sm:h-14 rounded-full bg-[#3054ff] group-hover:bg-[#1e3aff] flex items-center justify-center transition-colors">
                    <ArrowRight className="w-5 h-5 sm:w-7 sm:h-7 text-white" />
                  </span>
                </motion.button>
                <p className={`${type.caption} text-muted-foreground/80`}>
                  No credit card needed. One site free.
                </p>
              </motion.div>
            ) : awaitingModeChoice ? (
              /* Phase 33d — intent picker. Shown when the user pastes a URL
                 so they can choose whether to extract their own brand info
                 or treat the URL as a visual inspiration reference. */
              <motion.div
                key="mode-picker"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: EASE_CINEMATIC }}
                className="w-full max-w-xl mx-auto space-y-4"
              >
                <p className="text-sm text-muted-foreground text-center truncate">
                  <span className="text-muted-foreground/70 mr-1">URL:</span>
                  <span className="text-foreground/85">{pendingUrl}</span>
                </p>
                <p className="text-base text-foreground text-center font-medium">What would you like to do with this?</p>
                <div className="flex flex-col sm:flex-row gap-3">
                  {/* Primary: brand mode */}
                  <button
                    onClick={() => runExtraction(pendingUrl, "brand", pendingFiles)}
                    className="flex-1 flex items-center gap-3 px-5 py-4 rounded-2xl bg-card hover:bg-accent border border-border hover:border-foreground/30 transition-colors text-left group"
                  >
                    <span className="w-9 h-9 rounded-full bg-[#3054ff] group-hover:bg-[#1e3aff] flex items-center justify-center transition-colors shrink-0">
                      <Rocket className="w-4 h-4 text-white" aria-hidden />
                    </span>
                    <span>
                      <span className="block text-sm font-semibold text-foreground">Build this business&apos;s site</span>
                      <span className="block text-xs text-muted-foreground mt-0.5">Extract brand + industry info</span>
                    </span>
                    <span className="ml-auto text-[10px] font-bold uppercase tracking-wider text-[#3054ff] bg-[#3054ff]/10 px-2 py-1 rounded-full shrink-0">Recommended</span>
                  </button>
                  {/* Secondary: inspire mode */}
                  <button
                    onClick={() => runExtraction(pendingUrl, "inspire", pendingFiles)}
                    className="flex-1 flex items-center gap-3 px-5 py-4 rounded-2xl bg-card/60 hover:bg-card border border-border/70 hover:border-border transition-colors text-left group"
                  >
                    <span className="w-9 h-9 rounded-full bg-muted group-hover:bg-accent flex items-center justify-center transition-colors shrink-0">
                      <Sparkles className="w-4 h-4 text-muted-foreground" aria-hidden />
                    </span>
                    <span>
                      <span className="block text-sm font-semibold text-foreground">Inspired by this design</span>
                      <span className="block text-xs text-muted-foreground mt-0.5">Match the visual style only</span>
                    </span>
                  </button>
                </div>
                <button
                  onClick={() => { setAwaitingModeChoice(false); setPendingUrl(""); }}
                  className="w-full text-xs text-muted-foreground hover:text-foreground text-center transition-colors py-1"
                >
                  Cancel — type something else
                </button>
              </motion.div>
            ) : matchedDnaResult && inspireResult ? (
              /* Phase 33d — matched DNA result card. Shown after a successful
                 inspire extraction before advancing to the questionnaire. */
              <motion.div
                key="dna-card"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.4, ease: EASE_CINEMATIC }}
                className="w-full max-w-xl mx-auto p-7 rounded-2xl bg-card backdrop-blur-xl border border-border shadow-[0_8px_40px_rgba(0,0,0,0.06)] space-y-5"
              >
                <div className="space-y-1">
                  <p className={`${type.eyebrow}`}>Matched style</p>
                  <h3 className="font-display italic text-2xl text-foreground leading-snug">
                    {matchedDnaResult.label}
                  </h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{matchedDnaResult.feel}</p>
                </div>

                {/* Confidence bar */}
                <div className="space-y-1.5">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Style match confidence</span>
                    <span>{Math.round(matchedDnaResult.confidence * 100)}%</span>
                  </div>
                  <div className="h-1 rounded-full bg-muted overflow-hidden">
                    <motion.div
                      className="h-full rounded-full bg-foreground/70"
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.round(matchedDnaResult.confidence * 100)}%` }}
                      transition={{ duration: 0.6, ease: EASE_CINEMATIC, delay: 0.2 }}
                    />
                  </div>
                </div>

                <p className="text-[11px] text-muted-foreground leading-relaxed border-t border-border pt-4">
                  Custom 3D scenes and shaders won&apos;t be replicated — we&apos;ll match the vibe with lighter techniques.
                </p>

                <div className="flex flex-col sm:flex-row gap-3 pt-1">
                  <button
                    onClick={() => { void applyExtractionAndAdvance(pendingUrl, inspireResult!, pendingFiles, "inspire"); }}
                    className="flex-1 flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-foreground text-background font-semibold text-sm hover:bg-foreground/90 transition-colors"
                  >
                    Use this style
                    <ArrowRight className="w-4 h-4" aria-hidden />
                  </button>
                  <button
                    onClick={() => { setMatchedDnaResult(null); setInspireResult(null); runExtraction(pendingUrl, "brand", pendingFiles); }}
                    className="flex-1 text-sm text-muted-foreground hover:text-foreground transition-colors px-4 py-3 rounded-xl hover:bg-muted"
                  >
                    Pick a different style
                  </button>
                </div>
              </motion.div>
            ) : extracting ? (
              /* Phase 33c/d — extraction narration. Replaces the prompt
                 input while the brand-extract call is in flight. Steps
                 animate via setExtractStepIdx every 900ms. */
              <motion.div
                key="extract"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: EASE_CINEMATIC }}
                className="w-full max-w-xl mx-auto p-8 rounded-2xl bg-card backdrop-blur-xl border border-border shadow-[0_8px_40px_rgba(0,0,0,0.06)] space-y-4"
                role="status"
                aria-live="polite"
              >
                {EXTRACT_STEPS.map((label, i) => {
                  const status =
                    i < extractStepIdx ? "done" :
                    i === extractStepIdx ? "active" : "pending";
                  return (
                    <div
                      key={label}
                      className={`flex items-center gap-3 text-base transition-colors ${
                        status === "done"   ? "text-foreground" :
                        status === "active" ? "text-foreground" :
                        "text-muted-foreground/60"
                      }`}
                    >
                      {status === "done" ? (
                        <Check className="w-5 h-5 text-green-600" aria-hidden />
                      ) : status === "active" ? (
                        <motion.div
                          aria-hidden
                          className="w-5 h-5 rounded-full border-2 border-muted-foreground/30 border-t-foreground"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                      ) : (
                        <div aria-hidden className="w-5 h-5 rounded-full border border-border" />
                      )}
                      <span>{label}</span>
                    </div>
                  );
                })}
                {extractError && (
                  <div className="mt-4 flex items-start gap-2 text-sm text-amber-700 pt-4 border-t border-border">
                    <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" aria-hidden />
                    <span>{extractError}</span>
                  </div>
                )}
              </motion.div>
            ) : (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: EASE_CINEMATIC }}
                className="w-full space-y-6"
              >
                {/* Phase 40h (2026-05-21) — DetectiveInput now ships with the
                    "six-pack": Add Files, Plan-first toggle, voice dictation
                    (Web Speech API; hidden on Firefox), glowing Send when
                    unlocked, typewriter placeholder cycle, and a rotating
                    clickable suggestion below the bar. opts.files threads
                    image attachments through to handleSend / runExtraction
                    (both already accept files). opts.planMode is wired here:
                    on plan-first, we still call handleSend but the workspace
                    knows to hit /api/plan before committing the credit (see
                    the `planFirst` brief flag patched below). */}
                <DetectiveInput
                  autoFocus
                  onSubmit={(value, opts) => {
                    // Inspire-mode shortcut: if the user clicked "Switch to
                    // Inspired by this design" inside the input, we skip the
                    // separate mode-picker step.
                    if (opts?.inspireMode && looksLikeUrl(value.trim())) {
                      setPendingUrl(value.trim());
                      void runExtraction(value.trim(), "inspire", opts?.files);
                      return;
                    }
                    // Plan-first: stamp a flag onto the brief so the build
                    // pipeline calls /api/plan (cheap preview, no credit
                    // spent) before any /api/generate. Workspace surfaces
                    // the plan + a "Build this" confirm step.
                    if (opts?.planMode) {
                      void patchBrief({ planFirst: true });
                    }
                    void handleSend(value, opts?.files);
                  }}
                />
                <div className="flex items-center justify-between flex-wrap gap-3 text-sm">
                  <Link
                    href="/migrate"
                    className="text-muted-foreground hover:text-foreground inline-flex items-center gap-2 transition-colors"
                  >
                    <span>Already have a site?</span>
                    <span className="font-semibold underline underline-offset-2">Bring it over →</span>
                  </Link>
                  {/* Phase 34 — Build intent toggle. Business is default and stays
                      invisible to 90% of users. Project mode is one-click opt-in
                      for developers / designers who want a sandbox-style build
                      (cleaner source, editorial layout latitude, understated CTAs). */}
                  <button
                    type="button"
                    onClick={() => setBuildIntent((cur) => cur === "business" ? "project" : "business")}
                    className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
                    title={buildIntent === "project"
                      ? "Switch back to a business site build (default)"
                      : "Switch to a project / portfolio build — cleaner code, editorial layout, understated CTAs"}
                  >
                    <span className={`inline-block w-2 h-2 rounded-full transition-colors ${buildIntent === "project" ? "bg-foreground" : "bg-muted-foreground/40"}`} aria-hidden />
                    <span>
                      {buildIntent === "project"
                        ? <>Project mode <span className="underline underline-offset-2 font-semibold">on</span></>
                        : <>Building a portfolio? <span className="underline underline-offset-2 font-semibold">Switch to Project mode</span></>}
                    </span>
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {mounted && resumeName && (
          <motion.button
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0, transition: { delay: 0.3, duration: SHORT_S, ease: EASE_CINEMATIC } }}
            onClick={handleResume}
            className="group flex items-center gap-2 px-5 py-3 bg-card hover:bg-accent border border-border rounded-full text-muted-foreground hover:text-foreground text-sm backdrop-blur-sm transition-colors"
          >
            <span>Continue working on</span>
            <span className="text-foreground font-medium">{resumeName}</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </motion.button>
        )}
        </motion.div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          LIGHT MARKETING BODY — white → soft gray gradient
          ════════════════════════════════════════════════════════════════ */}
      <div className="relative bg-gradient-to-b from-background via-background to-muted text-foreground font-[family-name:var(--font-plus-jakarta-sans)]">
        {/* §2 — From sentence to site.
            Phase 43.2 (2026-05-21) — retired the SwiperSteps text cards.
            The most compelling answer to "how does this work?" is showing
            it actually working, so §2 is now a code-driven build demo
            that loops through the 3 stages (TYPE → PLAN → SITE) in ~12s.
            See components/hero/build-demo.tsx. SwiperSteps is still on
            disk for a quick revert if needed.
            STEPS data also unused for now — kept for the same revert path. */}
        <section
          id="how"
          className="relative px-4 py-16 sm:py-24 max-w-5xl mx-auto"
        >
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.94 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="text-center mb-10 sm:mb-14 space-y-4"
          >
            <h2 className={`${type.display.l} text-foreground`}>
              From sentence to site.
            </h2>
            <p className="text-lg max-w-xl mx-auto text-muted-foreground">
              Three steps. About twelve seconds to watch. About five minutes to ship.
            </p>
          </motion.div>
          <BuildDemo />
        </section>

        {/* §3 — Looks. Phase 43.6 (2026-05-21) — retired the palette grid
            + hover preview (Phase 43 / 43.3) in favor of the vercel-v0-
            style reference Marc shared: "Prompt → Application" pill arc
            above a full-bleed horizontal marquee of real Pebble template
            PNGs. Each tile is large enough to read as a real artifact.
            See components/hero/marquee-showcase.tsx.

            The DNAS const still lives in this file (used implicitly
            elsewhere via type / for the workspace plan phase) so we
            don't delete it. */}
        <section
          id="looks"
          ref={dnaSec.ref}
          className="relative pebble-dot-grid py-16 sm:py-24 overflow-hidden"
        >
          <motion.div
            className="text-center mb-10 sm:mb-12 space-y-4 px-4 max-w-3xl mx-auto"
            {...MOBILE_FADE_PROPS}
          >
            <h2 className={`${type.display.l} ${lightGradient}`}>
              What Pebble actually builds.
            </h2>
            <p className="text-lg max-w-xl mx-auto text-muted-foreground">
              Real marketing sites from real Pebble runs. Every one of these started as a single sentence.
            </p>
          </motion.div>

          <MarqueeShowcase />
        </section>

        {/* §4 — Perfect for. Phase 43: was a flat text-chip list — now
            an emotional 4-col photo grid using the same hero-craft
            photography. Each tile is a real person doing their craft
            with a clean label overlay. Mobile gets 2 cols + stacked
            (no sticky pin). */}
        <section
          ref={perfectSec.ref}
          className={cn("relative", !isMobile && "h-[180vh]")}
        >
          <div className={cn(
            "flex flex-col justify-center px-4 max-w-6xl mx-auto overflow-hidden",
            isMobile ? "py-16" : "sticky top-0 h-screen-safe",
          )}>
            <motion.div
              className="text-center mb-10 space-y-4 will-change-transform"
              {...(isMobile
                ? MOBILE_FADE_PROPS
                : { style: { y: perfectSec.headingY, scale: perfectSec.scale, opacity: perfectSec.opacity } })}
            >
              <h2 className={`${type.display.l} ${lightGradient}`}>
                Built for the people who do the work.
              </h2>
              <p className="text-lg max-w-xl mx-auto text-muted-foreground">
                Pebble tunes itself to your industry automatically.
              </p>
            </motion.div>

            <motion.div
              variants={STAGGER_PARENT}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true, amount: 0.15 }}
              className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 will-change-transform"
              {...(!isMobile && { style: { y: perfectSec.bodyY, opacity: perfectSec.opacity } })}
            >
              {PERFECT_FOR.map((p) => (
                <motion.div
                  key={p.label}
                  variants={STAGGER_CHILD}
                  whileHover={{ y: -4, scale: 1.02 }}
                  transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
                  className="relative group rounded-xl overflow-hidden aspect-[4/5] sm:aspect-square bg-muted shadow-[0_4px_20px_rgba(31,29,26,0.06)] hover:shadow-[0_12px_36px_rgba(31,29,26,0.14)] transition-shadow"
                  style={{
                    backgroundImage:    `url(${p.photo})`,
                    backgroundSize:     "cover",
                    backgroundPosition: "center",
                  }}
                  title={p.label}
                >
                  {/* Bottom gradient + label — keeps the photo readable
                      while ensuring the industry name reads at all sizes */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/75 via-black/30 to-transparent p-3 sm:p-4">
                    <span className="text-white text-xs sm:text-sm font-semibold tracking-tight drop-shadow">{p.label}</span>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* §5 — Takeoff moment. Phase 43.5 (2026-05-21) — retired the
            placeholder testimonial in favor of a launch animation that
            tees up the pricing section directly below. See
            components/hero/takeoff-moment.tsx. The component manages
            its own scroll-into-view trigger + reduced-motion fallback;
            here we just give it a wrapper with enough height to feel
            cinematic (full screen on desktop, ~70vh on mobile so it
            doesn't dominate). */}
        <section
          ref={quoteSec.ref}
          className={cn("relative", !isMobile && "h-[150vh]")}
        >
          <div className={cn(
            "overflow-hidden",
            isMobile ? "h-[70vh]" : "sticky top-0 h-screen-safe",
          )}>
            <TakeoffMoment scrollTo="#pricing" />
          </div>
        </section>

        {/* §6 — Pricing. Phase 43: mobile drops the sticky pin and the
            cards become whole-card click targets that expand on tap +
            fire an LED border pulse for a "feels good" interaction.
            The pinned desktop variant stays but is taller (240vh) so
            the accordion expansions fit inside the pin. */}
        <section
          id="pricing"
          ref={pricingSec.ref}
          className={cn("relative", !isMobile && "h-[240vh]")}
        >
          <div className={cn(
            "flex flex-col justify-center px-4 max-w-6xl mx-auto overflow-hidden",
            isMobile ? "py-16" : "sticky top-0 h-screen-safe",
          )}>
          <motion.div
            className="text-center mb-10 space-y-4 will-change-transform"
            {...(isMobile
              ? MOBILE_FADE_PROPS
              : { style: { y: pricingSec.headingY, scale: pricingSec.scale, opacity: pricingSec.opacity } })}
          >
            <h2 className={`${type.display.l} ${lightGradient}`}>
              Simple pricing.
            </h2>
            <p className="text-lg max-w-xl mx-auto text-muted-foreground">
              Start free. Upgrade when you need more sites or a custom domain.
            </p>

            {/* Billing toggle — animated thumb slides between Monthly / Yearly. */}
            <div className="inline-flex items-center gap-1 p-1 rounded-full bg-muted border border-border mt-4">
              {(["monthly", "yearly"] as const).map((opt) => (
                <button
                  key={opt}
                  onClick={() => setBilling(opt)}
                  className="relative px-5 py-1.5 text-sm font-medium"
                >
                  {billing === opt && (
                    <motion.div
                      layoutId="billing-thumb"
                      className="absolute inset-0 bg-white rounded-full shadow-[0_2px_8px_rgba(0,0,0,0.08)]"
                      transition={{ type: "spring", stiffness: 400, damping: 30 }}
                    />
                  )}
                  <span className={`relative z-10 capitalize ${billing === opt ? "text-foreground" : "text-muted-foreground/80"}`}>
                    {opt}
                    {opt === "yearly" && (
                      <span className="ml-1.5 text-[10px] font-semibold text-[#3054ff] uppercase tracking-wider">
                        save 17%
                      </span>
                    )}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>

          <motion.div
            className="will-change-transform"
            {...(!isMobile && { style: { y: pricingSec.bodyY, opacity: pricingSec.opacity } })}
          >
            {activePlan && (
              <p className={`${type.mono} text-center text-muted-foreground mb-4`}>
                You&apos;re currently on the <strong className="text-foreground">{activePlan}</strong> plan
              </p>
            )}

            {/* Phase 43.4 — Plan-picker micro-quiz. Two questions, three
                + two pill buttons. Answering both populates a
                "recommended for you" badge on the matching tier card
                + pulses its LED border. Honest + useful, not a sales
                gimmick — the recommendation logic mirrors the real
                tier mechanics. */}
            <div className="max-w-3xl mx-auto mb-8 sm:mb-10">
              <div className="rounded-2xl border border-border bg-white/70 backdrop-blur-sm shadow-[0_4px_18px_rgba(31,29,26,0.05)] p-5 sm:p-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
                  <p className="text-xs uppercase tracking-[0.14em] font-semibold text-muted-foreground">
                    Not sure which plan? Two quick questions.
                  </p>
                  {recommendedTier && (
                    <motion.span
                      key={recommendedTier}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ duration: 0.3, ease: EASE_CINEMATIC }}
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#3054ff]/10 text-[#3054ff] text-xs font-semibold"
                    >
                      <Sparkles className="w-3 h-3" aria-hidden />
                      We recommend {recommendedTier}
                    </motion.span>
                  )}
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">How many sites?</p>
                    <div className="flex flex-wrap gap-1.5">
                      {([
                        { v: "one",  label: "Just 1"      },
                        { v: "few",  label: "A handful"   },
                        { v: "many", label: "Lots"        },
                      ] as const).map((opt) => (
                        <button
                          key={opt.v}
                          type="button"
                          onClick={() => setQuizSites(opt.v)}
                          className={cn(
                            "px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-150",
                            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
                            quizSites === opt.v
                              ? "bg-foreground text-background"
                              : "bg-muted/60 text-foreground/80 hover:bg-muted hover:text-foreground",
                          )}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Custom domain?</p>
                    <div className="flex flex-wrap gap-1.5">
                      {([
                        { v: "no",  label: "Not yet" },
                        { v: "yes", label: "Yes"     },
                      ] as const).map((opt) => (
                        <button
                          key={opt.v}
                          type="button"
                          onClick={() => setQuizDomain(opt.v)}
                          className={cn(
                            "px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-150",
                            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
                            quizDomain === opt.v
                              ? "bg-foreground text-background"
                              : "bg-muted/60 text-foreground/80 hover:bg-muted hover:text-foreground",
                          )}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <motion.div
              variants={STAGGER_PARENT}
              initial="hidden"
              whileInView="show"
              onViewportEnter={() => setPricingInView(true)}
              viewport={{ once: true, amount: 0.1 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10 items-stretch"
            >
              {PRICING_TIERS.map((tier) => {
                const isFree     = tier.monthly === 0;
                const isContact  = tier.monthly === null;
                const headlinePrice = isContact
                  ? "Let's talk"
                  : isFree
                    ? "Free"
                    : billing === "monthly"
                      ? `$${tier.monthly}`
                      : `$${Math.round((tier.yearly ?? 0) / 12)}`;
                const period = isContact ? "" : isFree ? "forever" : "/mo";
                const subtext = isContact
                  ? "Custom pricing"
                  : isFree
                    ? "No card needed."
                    : billing === "yearly"
                      ? `$${tier.yearly} billed annually`
                      : `Billed monthly`;

                const isExpanded = expandedTiers.has(tier.name);
                // Phase 43.4 — count-up lookup (hooks called at the top
                // of the component, indexed by tier name). For Free /
                // Enterprise we still render the static string label.
                const animatedPrice = priceTickers[tier.name] ?? 0;
                const showCountUp   = !isContact && !isFree;
                return (
                  <motion.div
                    key={tier.name}
                    variants={STAGGER_CHILD}
                    onClick={() => toggleTier(tier.name)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        toggleTier(tier.name);
                      }
                    }}
                    role="button"
                    tabIndex={0}
                    aria-expanded={isExpanded}
                    aria-label={`${tier.name} plan — tap to ${isExpanded ? "collapse" : "see all features"}`}
                    whileHover={{ y: -4 }}
                    whileTap={{ scale: 0.985 }}
                    transition={{ duration: 0.2, ease: EASE_CINEMATIC }}
                    className={cn(
                      "relative p-6 rounded-2xl flex flex-col cursor-pointer select-none",
                      "transition-shadow duration-300",
                      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2",
                      tier.featured
                        ? "bg-card border-2 border-[#3054ff] shadow-[0_12px_32px_rgba(48,84,255,0.18)] hover:shadow-[0_18px_44px_rgba(48,84,255,0.26)] lg:scale-[1.03] lg:-translate-y-2"
                        : "bg-card border border-border hover:border-foreground/30 hover:shadow-[0_12px_32px_rgba(31,29,26,0.10)]",
                      ledTier === tier.name && "tier-led-pulse",
                    )}
                  >
                    {tier.featured && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-[#3054ff] text-white text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap">
                        Most popular
                      </div>
                    )}

                    {/* Phase 43 — chevron at top-right indicates expandable
                        state. Replaces the verbose "See all features"
                        button row below. */}
                    <motion.span
                      aria-hidden
                      animate={{ rotate: isExpanded ? 180 : 0 }}
                      transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
                      className="absolute top-4 right-4 inline-flex w-7 h-7 items-center justify-center rounded-full text-muted-foreground/70 hover:text-foreground bg-muted/60 text-sm leading-none"
                    >
                      ▾
                    </motion.span>

                    <div className={`${type.eyebrow} mb-2 pr-8`}>{tier.name}</div>

                    <div className="mb-4">
                      <AnimatePresence mode="wait" initial={false}>
                        <motion.div
                          key={`${tier.name}-${billing}`}
                          initial={{ opacity: 0, y: 8 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -8 }}
                          transition={{ duration: 0.22, ease: EASE_CINEMATIC }}
                          className="flex items-baseline gap-1"
                        >
                          <span className={type.display.m}>
                            {showCountUp ? `$${animatedPrice}` : headlinePrice}
                          </span>
                          {period && <span className="text-sm text-muted-foreground/80">{period}</span>}
                        </motion.div>
                      </AnimatePresence>
                      <div className="text-xs text-muted-foreground/70 mt-1 h-4">{subtext}</div>
                    </div>

                    <p className="text-sm text-muted-foreground leading-relaxed mb-5">{tier.desc}</p>

                    <ul className="space-y-2 text-sm text-foreground/75 mb-4 flex-1">
                      {tier.highlights.map((f) => (
                        <li key={f} className="flex items-start gap-2">
                          <span className="text-[#3054ff] mt-0.5 shrink-0">✓</span>
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>

                    <AnimatePresence initial={false}>
                      {expandedTiers.has(tier.name) && (
                        <motion.div
                          key="details"
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.25, ease: EASE_CINEMATIC }}
                          className="overflow-hidden"
                        >
                          <div className="space-y-4 pt-2 pb-4 border-t border-border">
                            {tier.details.map((cat) => (
                              <div key={cat.category}>
                                <div className="text-[10px] uppercase tracking-wider text-muted-foreground/75 mb-2 mt-3">
                                  {cat.category}
                                </div>
                                <ul className="space-y-1.5 text-sm text-foreground/75">
                                  {cat.items.map((item) => (
                                    <li key={item} className="flex items-start gap-2">
                                      <span className="text-[#3054ff] mt-0.5 shrink-0">✓</span>
                                      <span>{item}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {(() => {
                      const isCurrent = activePlan && activePlan === tier.stripePlan;
                      const isLoading = stripeLoading === tier.name;
                      const label = isCurrent
                        ? "Current plan"
                        : isLoading
                          ? "Redirecting…"
                          : tier.cta;
                      const buttonClass = `block w-full text-center text-sm font-medium py-2.5 rounded-full transition-colors disabled:opacity-60 ${
                        isCurrent
                          ? "bg-muted hover:bg-muted/70 text-foreground"
                          : tier.featured
                            ? "bg-[#3054ff] hover:bg-[#2040e0] text-white"
                            : "bg-muted hover:bg-muted/70 text-foreground"
                      }`;

                      // Phase 43 — stopPropagation so clicking the CTA
                      // doesn't ALSO toggle the card expansion (the whole
                      // card is now a click target for toggle/expand).
                      if (tier.ctaHref) {
                        return (
                          <>
                            <a
                              href={tier.ctaHref}
                              onClick={(e) => e.stopPropagation()}
                              className={buttonClass}
                            >
                              {label}
                            </a>
                            {stripeErrorTierId === tier.name && stripeError && (
                              <p className={`${type.body.s} text-destructive mt-2 text-center`}>{stripeError}</p>
                            )}
                          </>
                        );
                      }
                      return (
                        <>
                          <button
                            type="button"
                            onClick={(e) => { e.stopPropagation(); handleChoosePlan(tier); }}
                            disabled={isLoading}
                            className={buttonClass}
                          >
                            {label}
                          </button>
                          {stripeErrorTierId === tier.name && stripeError && (
                            <p className={`${type.body.s} text-destructive mt-2 text-center`}>{stripeError}</p>
                          )}
                        </>
                      );
                    })()}
                  </motion.div>
                );
              })}
            </motion.div>

          </motion.div>
          </div>
        </section>

        {/* §7 — Final CTA. Phase 43.1 (2026-05-21) — stripped to a pure
            emotional finale per Marc's plan. The page now has a real
            ending: big rotating multilingual Pebble wordmark, one line
            of copy, and a single button that scrolls back to the hero
            input. The old duplicate PromptInputBox was UI redundancy —
            same input twice on the same page. Conversion lives at the
            top; this section just closes the loop. */}
        <section
          id="start"
          ref={ctaSec.ref}
          className={cn("relative", !isMobile && "h-[140vh]")}
        >
          <div className={cn(
            "flex flex-col items-center justify-center gap-10 px-4 max-w-3xl mx-auto text-center overflow-hidden",
            isMobile ? "py-20" : "sticky top-0 h-screen-safe",
          )}>
            {/* Big rotating multilingual logo — the centerpiece */}
            <motion.div
              className="will-change-transform"
              {...(isMobile
                ? MOBILE_FADE_PROPS
                : { style: { y: ctaSec.headingY, scale: ctaSec.scale, opacity: ctaSec.opacity } })}
            >
              <RotatingPebbleLogo
                shimmerStyle={shimmerForegroundStyle}
                className="text-6xl sm:text-8xl lg:text-9xl"
              />
            </motion.div>

            {/* One line + one CTA */}
            <motion.div
              className="space-y-8 will-change-transform"
              {...(isMobile
                ? MOBILE_FADE_PROPS
                : { style: { y: ctaSec.bodyY, opacity: ctaSec.opacity } })}
            >
              <p className={`font-[family-name:var(--font-cormorant)] italic text-2xl sm:text-3xl text-foreground/85 max-w-xl mx-auto`}>
                Your idea is one paragraph away.
              </p>
              <motion.button
                type="button"
                onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
                whileHover={{ scale: 1.03, y: -2 }}
                whileTap={{ scale: 0.97 }}
                transition={{ duration: 0.2, ease: EASE_CINEMATIC }}
                className="group inline-flex items-center gap-3 pl-6 sm:pl-8 pr-2 sm:pr-3 py-1.5 sm:py-2 bg-foreground rounded-full hover:opacity-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3054ff] focus-visible:ring-offset-2"
              >
                <span className="font-semibold text-base sm:text-lg text-background">Take me back to the start</span>
                <span className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#3054ff] group-hover:bg-[#1e3aff] flex items-center justify-center transition-colors">
                  <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 text-white -rotate-90" aria-hidden />
                </span>
              </motion.button>
            </motion.div>
          </div>
        </section>

        {/* §8 — Footer. */}
        <footer className="border-t border-border px-4 py-12 bg-background">
          <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between gap-8">
            <div className="space-y-2">
              <Link href="/" className="inline-flex items-center">
                <RotatingPebbleLogo shimmerStyle={shimmerForegroundStyle} className="text-3xl" />
              </Link>
              <p className="text-sm text-muted-foreground/80 max-w-xs">
                A website you understand, built with you, not just for you.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-12 text-sm">
              <div className="space-y-3">
                <div className={`${type.eyebrow}`}>Product</div>
                <a href="#pricing" className="block text-muted-foreground hover:text-foreground">Pricing</a>
                <Link href="/help"    className="block text-muted-foreground hover:text-foreground">Help</Link>
              </div>
              <div className="space-y-3">
                <div className={`${type.eyebrow}`}>Legal</div>
                <Link href="/privacy" className="block text-muted-foreground hover:text-foreground">Privacy</Link>
                <Link href="/terms"   className="block text-muted-foreground hover:text-foreground">Terms</Link>
              </div>
              <div className="space-y-3">
                <div className={`${type.eyebrow}`}>Account</div>
                <Link href="/login"  className="block text-muted-foreground hover:text-foreground">Log in</Link>
                <Link href="/signup" className="block text-muted-foreground hover:text-foreground">Sign up</Link>
              </div>
            </div>
          </div>
          <div className="max-w-6xl mx-auto mt-12 pt-8 border-t border-border/70 text-xs text-muted-foreground/70">
            © 2026 Pebble. Made for people who want to actually understand their website.
          </div>
        </footer>
      </div>
    </div>
  );
}
