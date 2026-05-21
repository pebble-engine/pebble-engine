"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence, MotionConfig, useScroll, useTransform } from "framer-motion";
import { ArrowRight, Sparkles, Palette, Rocket, Check, AlertCircle } from "lucide-react";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
import { BackgroundCarousel } from "@/components/hero/background-carousel";
import { DetectiveInput } from "@/components/hero/detective-input";
import {
  patchBrief,
  getUserProfile,
  getLastBuild,
  getBrief,
  deriveProjectName,
} from "@/lib/state";
import { SHORT_S, EASE_CINEMATIC } from "@/lib/motion";
import { type } from "@/lib/type";
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

const DNAS = [
  { label: "Swiss Magazine",        feel: "Editorial print. Vignelli-meets-Pentagram. Quiet authority." },
  { label: "Cinematic IMAX",        feel: "Movie poster meets Tesla product page. Widescreen, dramatic." },
  { label: "Garden Press",          feel: "Kinfolk × botanical letterpress almanac. Quiet, premium, considered." },
  { label: "Velvet Lounge",         feel: "Late-night Manhattan jazz bar. Rich, intimate, candlelit." },
  { label: "Tactile Y2K",           feel: "Early-2000s Apple × a really good neighborhood bakery. Soft, organic." },
  { label: "Industrial Freight",    feel: "Shipping manifest × heavy-equipment catalog. Utilitarian, blocky." },
  { label: "Marina",                feel: "Hinckley Yachts × Hamptons summer journal. Clean, salt-air premium." },
  { label: "Postmodern Maximalist", feel: "David Carson × club flyer. Loud, layered, intentionally chaotic." },
];

const BUSINESS_TYPES = [
  "Coffee shops + cafés",
  "Photographers + videographers",
  "Restaurants + food trucks",
  "Coaches + consultants",
  "Law + accounting practices",
  "Trades + contractors",
  "Personal portfolios",
  "Salons + boutique shops",
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

const NAV_ITEMS = [
  { label: "How it works", href: "#how" },
  { label: "Looks",        href: "#looks" },
  { label: "Pricing",      href: "#pricing" },
  { label: "Start",        href: "#start" },
];

const shimmerSilverStyle = {
  backgroundImage:
    "linear-gradient(90deg, #9ca3af 0%, #e5e7eb 25%, #ffffff 50%, #e5e7eb 75%, #9ca3af 100%)",
  backgroundSize: "200% auto",
};

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
 * Glassmorphic top nav. Fixed pill at top-center; items use an animated
 * silver gradient (`shimmerSilverStyle`) clipped to the text. Anchors
 * scroll smoothly into the corresponding section.
 */
function TopNavBar() {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const id = href.replace("#", "");
    if (id === "") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    } else {
      document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

  return (
    <>
      {/* ── Top-left: rotating multilingual Pebble wordmark ── */}
      <motion.div
        initial={{ opacity: 0, x: -16 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="fixed top-4 left-6 z-40"
      >
        <Link
          href="/"
          onClick={(e) => handleClick(e, "#")}
          className="inline-flex items-center"
        >
          <RotatingPebbleLogo shimmerStyle={shimmerForegroundStyle} className="text-2xl" />
        </Link>
      </motion.div>

      {/* ── Center: page-anchor pill (no wordmark) ── */}
      <motion.nav
        initial={{ opacity: 0, y: -16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="fixed top-4 left-1/2 -translate-x-1/2 z-40"
        aria-label="Page navigation"
      >
        <MotionConfig reducedMotion="never">
          <div className="flex items-center gap-2 px-3 py-2 rounded-full bg-card/60 backdrop-blur-2xl border border-border shadow-[0_4px_32px_rgba(31,29,26,0.08),inset_0_1px_0_rgba(255,255,255,0.6)]">
            {NAV_ITEMS.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={(e) => handleClick(e, item.href)}
                className="px-5 py-2 rounded-full hover:bg-accent transition-colors text-base font-bold"
              >
                <motion.span
                  className="bg-clip-text text-transparent"
                  style={shimmerForegroundStyle}
                  animate={{ backgroundPosition: ["0% 0%", "200% 0%"] }}
                  transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                >
                  {item.label}
                </motion.span>
              </a>
            ))}
          </div>
        </MotionConfig>
      </motion.nav>
    </>
  );
}

/**
 * Two-layer scroll-tied parallax per section. The heading layer moves faster
 * (180px range) than the body (60px) to create depth as the user scrolls
 * through. Opacity fades content in/out at the section edges so each one
 * reads as its own moment.
 */
function useParallaxSection() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  return {
    ref,
    // Phase 40 (2026-05-21) — Marc reported parallax "breaking when starting
    // to scroll down". Root cause was magnitude collisions: 180px heading
    // lift + 60px body shift + global hero lift + hero fade + dual blob
    // shifts all firing simultaneously caused jank on fast scroll. Softened
    // magnitudes by ~3x. Subtle motion still reads as parallax, but the
    // visual chunking is gone.
    headingY: useTransform(scrollYProgress, [0, 1], [60, -60]),
    bodyY:    useTransform(scrollYProgress, [0, 1], [20, -20]),
    opacity:  useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [0, 1, 1, 0]),
  };
}

export function WelcomePhase({ onAdvance }: Props) {
  const router = useRouter();
  const [firstName, setFirstName] = useState<string | null>(null);
  const [resumeName, setResumeName] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);
  const [wordIdx, setWordIdx] = useState(0);
  const [started, setStarted] = useState(false);
  const [billing, setBilling] = useState<"monthly" | "yearly">("monthly");
  const [expandedTiers, setExpandedTiers] = useState<Set<string>>(new Set());
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
  const sentenceSec = useParallaxSection();
  const dnaSec      = useParallaxSection();
  const perfectSec  = useParallaxSection();
  const quoteSec    = useParallaxSection();
  const pricingSec  = useParallaxSection();
  const ctaSec      = useParallaxSection();

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
      const res = await extractBrand(url, mode);
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
      <TopNavBar />

      {/* ════════════════════════════════════════════════════════════════
          LIGHT HERO (cream/sand background, charcoal text)
          ════════════════════════════════════════════════════════════════ */}
      <section className="relative bg-background text-foreground overflow-hidden">
        {/* Background carousel — real Pebble builds, ken-burns parallax */}
        <BackgroundCarousel />
        {/* Decorative blobs — softer pastel pulse over the carousel + bg */}
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
          className="relative z-10 min-h-screen flex flex-col items-center justify-center text-center px-4 max-w-5xl mx-auto py-20 space-y-10 will-change-transform"
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
                  whileTap={{ scale: 0.98 }}
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
                  className="group flex items-center gap-4 pl-10 pr-3 py-3 bg-foreground rounded-full"
                >
                  <span className="font-semibold text-2xl text-background">Start Building Free</span>
                  <span className="w-14 h-14 rounded-full bg-[#3054ff] group-hover:bg-[#1e3aff] flex items-center justify-center transition-colors">
                    <ArrowRight className="w-7 h-7 text-white" />
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
                {/* Phase 40 — DetectiveInput replaces the generic chat-style
                    PromptInputBox. Detects URL vs industry phrase vs prose as
                    the user types and surfaces a status line. No fake "plan/
                    generate/attach" buttons that other AI builders ship. */}
                <DetectiveInput
                  autoFocus
                  onSubmit={(value, opts) => {
                    // Inspire-mode shortcut: if the user clicked "Switch to
                    // Inspired by this design" inside the input, we skip the
                    // separate mode-picker step.
                    if (opts?.inspireMode && looksLikeUrl(value.trim())) {
                      setPendingUrl(value.trim());
                      void runExtraction(value.trim(), "inspire");
                      return;
                    }
                    void handleSend(value);
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
            Phase 40c (2026-05-21) — this is the cinematic moment Marc was
            asking for. The hero recedes (scale 0.97 + fade 0.6) as the
            user scrolls; this section then enters with weight:
            - Heading: scale 0.92 → 1, y 32 → 0, opacity 0 → 1, big spring
            - Subhead: same shape, 0.12s delay, smaller magnitude
            - Step cards: stagger 0.1s each, scale 0.95 → 1, y 24 → 0
            - All viewport-driven via whileInView (fires once when 30% in).
            The section-tied parallax (sentenceSec) is REMOVED here in
            favor of the more dramatic whileInView entrance. */}
        <section
          id="how"
          ref={sentenceSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-6xl mx-auto py-16"
        >
          {/* Phase 40d — viewport.amount lowered from 0.3 → 0.05 so the
              entrance fires the moment the section's top crosses into view,
              not when 30% is already showing. Magnitudes bumped: scale
              0.92 → 0.82 (more dramatic zoom-in), y 32 → 64, duration 0.9 →
              1.1s. The user clearly sees the heading LAND with weight
              instead of just appearing already-there. */}
          <motion.div
            initial={{ opacity: 0, y: 64, scale: 0.82 }}
            whileInView={{ opacity: 1, y: 0, scale: 1 }}
            viewport={{ once: true, amount: 0.05 }}
            transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
            className="text-center mb-16 space-y-4 will-change-transform"
          >
            <h2 className={`${type.display.l} ${lightGradient}`}>
              From sentence to site.
            </h2>
            <motion.p
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.05 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1], delay: 0.25 }}
              className="text-lg max-w-xl mx-auto text-muted-foreground"
            >
              Three steps from a paragraph about your business to a real, editable website.
            </motion.p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {STEPS.map((step, i) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 48, scale: 0.88 }}
                whileInView={{ opacity: 1, y: 0, scale: 1 }}
                viewport={{ once: true, amount: 0.05 }}
                transition={{
                  duration: 0.85,
                  ease: [0.22, 1, 0.36, 1],
                  delay: 0.45 + i * 0.15,
                }}
                className="p-8 rounded-2xl bg-card border border-border will-change-transform"
              >
                <step.Icon className="w-8 h-8 text-[#3054ff] mb-6" />
                <h3 className={`${type.heading.l} mb-3`}>{step.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{step.body}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* §3 — DNA showcase. */}
        <section
          id="looks"
          ref={dnaSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-6xl mx-auto py-16"
        >
          <motion.div
            style={{ y: dnaSec.headingY, opacity: dnaSec.opacity }}
            className="text-center mb-16 space-y-4 will-change-transform"
          >
            <h2 className={`${type.display.l} ${lightGradient}`}>
              The looks Pebble can wear.
            </h2>
            <p className="text-lg max-w-2xl mx-auto text-muted-foreground">
              Every Pebble build picks from an over-specified visual personality — so two sites for the same industry come out feeling like they were made by different studios.
            </p>
          </motion.div>

          <motion.div
            style={{ y: dnaSec.bodyY, opacity: dnaSec.opacity }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 will-change-transform"
          >
            {DNAS.map((dna) => (
              <div
                key={dna.label}
                className="p-6 rounded-xl bg-card border border-border hover:border-[#3054ff]/40 transition-colors"
              >
                <h3 className={`${type.heading.s} mb-2`}>{dna.label}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{dna.feel}</p>
              </div>
            ))}
          </motion.div>
        </section>

        {/* §4 — Perfect for. */}
        <section
          ref={perfectSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-5xl mx-auto py-16"
        >
          <motion.div
            style={{ y: perfectSec.headingY, opacity: perfectSec.opacity }}
            className="text-center mb-16 space-y-4 will-change-transform"
          >
            <h2 className={`${type.display.l} ${lightGradient}`}>
              Perfect for…
            </h2>
            <p className="text-lg max-w-xl mx-auto text-muted-foreground">
              Pebble routes industry-specific design choices automatically. These are the businesses we&apos;re tuned for today.
            </p>
          </motion.div>

          <motion.div
            style={{ y: perfectSec.bodyY, opacity: perfectSec.opacity }}
            className="flex flex-wrap justify-center gap-3 will-change-transform"
          >
            {BUSINESS_TYPES.map((t) => (
              <span
                key={t}
                className="px-5 py-3 rounded-full bg-card border border-border text-foreground/85 text-sm sm:text-base"
              >
                {t}
              </span>
            ))}
          </motion.div>
        </section>

        {/* §5 — Testimonial. */}
        <section
          ref={quoteSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-3xl mx-auto text-center py-16"
        >
          <motion.blockquote
            style={{ y: quoteSec.headingY, opacity: quoteSec.opacity }}
            className="space-y-6 will-change-transform"
          >
            <p className={`font-[family-name:var(--font-cormorant)] italic text-3xl sm:text-4xl leading-[1.2] ${lightGradient}`}>
              &ldquo;We&apos;re building Pebble in public. A real testimonial from a real beta user will land here once their site is shipped. We&apos;d rather wait than make one up.&rdquo;
            </p>
            <footer className="text-sm text-muted-foreground/80">— Pebble, May 2026</footer>
          </motion.blockquote>
        </section>

        {/* §6 — Pricing tease with monthly/yearly toggle. */}
        <section
          id="pricing"
          ref={pricingSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-6xl mx-auto py-16"
        >
          <motion.div
            style={{ y: pricingSec.headingY, opacity: pricingSec.opacity }}
            className="text-center mb-10 space-y-4 will-change-transform"
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
            style={{ y: pricingSec.bodyY, opacity: pricingSec.opacity }}
            className="will-change-transform"
          >
            {activePlan && (
              <p className={`${type.mono} text-center text-muted-foreground mb-4`}>
                You&apos;re currently on the <strong className="text-foreground">{activePlan}</strong> plan
              </p>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10 items-stretch">
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

                return (
                  <div
                    key={tier.name}
                    className={`relative p-6 rounded-2xl flex flex-col transition-transform ${
                      tier.featured
                        ? "bg-card border-2 border-[#3054ff] shadow-[0_12px_32px_rgba(48,84,255,0.18)] lg:scale-[1.03] lg:-translate-y-2"
                        : "bg-card border border-border"
                    }`}
                  >
                    {tier.featured && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-[#3054ff] text-white text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap">
                        Most popular
                      </div>
                    )}

                    <div className={`${type.eyebrow} mb-2`}>{tier.name}</div>

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
                          <span className={type.display.m}>{headlinePrice}</span>
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

                    <button
                      type="button"
                      onClick={() => toggleTier(tier.name)}
                      aria-expanded={expandedTiers.has(tier.name)}
                      className="flex items-center justify-center gap-1.5 text-xs font-medium text-muted-foreground/80 hover:text-foreground mb-4 transition-colors"
                    >
                      {expandedTiers.has(tier.name) ? "Hide all features" : "See all features"}
                      <motion.span
                        animate={{ rotate: expandedTiers.has(tier.name) ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                        className="inline-block"
                      >
                        ▾
                      </motion.span>
                    </button>

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

                      if (tier.ctaHref) {
                        return (
                          <>
                            <a href={tier.ctaHref} className={buttonClass}>{label}</a>
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
                            onClick={() => handleChoosePlan(tier)}
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
                  </div>
                );
              })}
            </div>

          </motion.div>
        </section>

        {/* §7 — Final CTA. */}
        <section
          id="start"
          ref={ctaSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-3xl mx-auto text-center py-16 space-y-10"
        >
          <motion.div
            style={{ y: ctaSec.headingY, opacity: ctaSec.opacity }}
            className="space-y-4 will-change-transform"
          >
            <p className={`${type.eyebrow}`}>Ready to build?</p>
            <h2 className={`${type.display.l} ${lightGradient}`}>
              Tell me what you&apos;re thinking.
            </h2>
          </motion.div>

          <motion.div
            style={{ y: ctaSec.bodyY, opacity: ctaSec.opacity }}
            className="space-y-10 will-change-transform"
          >
            <PromptInputBox
              onSend={handleSend}
              placeholder="Example: A site for my new coffee shop — menu, hours, and a way to order pickup."
            />

            <p className="text-sm text-muted-foreground/80">
              You&apos;ll see exactly what I&apos;m doing every step of the way. Nothing is final until you say it is.
            </p>
          </motion.div>
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
