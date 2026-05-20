"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence, MotionConfig, useScroll, useTransform } from "framer-motion";
import { ArrowRight, Sparkles, Palette, Rocket } from "lucide-react";
import { PromptInputBox } from "@/components/ui/ai-prompt-box";
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
import { createCheckoutSession, fetchSubscription, type SubscriptionState } from "@/lib/api";

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

const ROTATING_WORDS = ["future", "business", "vision", "path"] as const;

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

const darkGradient =
  "bg-gradient-to-b from-white via-white to-[#b4c0ff] bg-clip-text text-transparent";
const lightGradient = "text-[#1a1a1a]";

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
    <motion.nav
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-4 left-1/2 -translate-x-1/2 z-40"
      aria-label="Page navigation"
    >
      <MotionConfig reducedMotion="never">
        <div className="flex items-center gap-1 pl-4 pr-2 py-1.5 rounded-full bg-stone-900/40 backdrop-blur-xl border border-white/15 shadow-[0_8px_32px_rgba(0,0,0,0.35)]">
          <Link
            href="/"
            onClick={(e) => handleClick(e, "#")}
            className="px-2 py-1 mr-1 text-lg font-semibold bg-gradient-to-b from-white via-white to-[#b4c0ff] bg-clip-text text-transparent"
          >
            Pebble.
          </Link>
          <div aria-hidden className="w-px h-5 bg-white/20 mx-1" />
          {NAV_ITEMS.map((item) => (
            <a
              key={item.href}
              href={item.href}
              onClick={(e) => handleClick(e, item.href)}
              className="px-4 py-2 rounded-full hover:bg-white/10 transition-colors text-sm font-medium"
            >
              <motion.span
                className="bg-clip-text text-transparent"
                style={shimmerSilverStyle}
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
    headingY: useTransform(scrollYProgress, [0, 1], [180, -180]),
    bodyY:    useTransform(scrollYProgress, [0, 1], [60, -60]),
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
    try {
      const { url } = await createCheckoutSession(tier.stripePlan);
      window.location.href = url;
    } catch (err) {
      setStripeError(err instanceof Error ? err.message : "Something went wrong. Try again.");
      setStripeLoading(null);
    }
  };

  // Parallax — document-scroll tied transforms. Blobs move slower than
  // scroll (depth), hero text lifts gently as you leave the hero behind.
  const { scrollY } = useScroll();
  const blobYTop      = useTransform(scrollY, [0, 1000], [0, -180]);
  const blobYBottom   = useTransform(scrollY, [0, 1000], [0, -300]);
  const heroLift      = useTransform(scrollY, [0, 800], [0, -120]);
  const heroFadeOut   = useTransform(scrollY, [200, 700], [1, 0.4]);

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

  const handleSend = (message: string, files?: File[]) => {
    if (typeof window === "undefined") return;
    // 2026-05-20 Phase 15a: derive a real business_name from the first
    // sentence of the idea text instead of hardcoding "Untitled Project".
    // The user can rename via the top nav later, but the default should
    // be recognisable (and produce a useful build slug).
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
    <div className="relative w-full font-[family-name:var(--font-instrument-sans)]">
      <TopNavBar />

      {/* ════════════════════════════════════════════════════════════════
          DARK HERO
          ════════════════════════════════════════════════════════════════ */}
      <section className="relative bg-black text-white overflow-hidden">
        {/* Decorative blobs — parallax (move slower than scroll). */}
        <motion.div
          aria-hidden
          style={{ y: blobYTop }}
          className="pointer-events-none absolute -top-[10%] left-[20%] w-[600px] h-[600px] bg-blue-900/20 blur-[120px] mix-blend-screen will-change-transform"
        />
        <motion.div
          aria-hidden
          style={{ y: blobYBottom }}
          className="pointer-events-none absolute bottom-0 right-[15%] w-[500px] h-[500px] bg-indigo-900/20 blur-[120px] mix-blend-screen will-change-transform"
        />

        <motion.div
          style={{ y: heroLift, opacity: heroFadeOut }}
          className="relative z-10 min-h-screen flex flex-col items-center justify-center text-center px-4 max-w-5xl mx-auto py-20 space-y-10 will-change-transform"
        >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-baseline justify-center gap-2"
        >
          <span className="text-white/60 text-lg sm:text-xl">welcome to</span>
          <span className={`text-2xl sm:text-3xl font-semibold ${darkGradient}`}>Pebble.</span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, scale: 0.92 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.6, ease: EASE_CINEMATIC }}
          className={`font-semibold text-5xl sm:text-7xl lg:text-[96px] leading-[0.95] tracking-tighter ${darkGradient}`}
        >
          Let&apos;s build your{" "}
          <MotionConfig reducedMotion="never">
            <span className="relative inline-block align-baseline">
              <span aria-hidden className="invisible">business</span>
              <AnimatePresence mode="wait">
                <motion.span
                  key={ROTATING_WORDS[wordIdx]}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.5, ease: EASE_CINEMATIC }}
                  className={`absolute left-0 top-0 ${darkGradient}`}
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
          className="text-lg sm:text-xl leading-[1.65] text-white max-w-xl"
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
              <motion.button
                key="cta"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, ease: EASE_CINEMATIC }}
                onClick={handleStartClick}
                className="group flex items-center gap-3 pl-6 pr-2 py-2 bg-white rounded-full transition-shadow duration-200 hover:shadow-[0_0_20px_rgba(255,255,255,0.3)]"
              >
                <span className="font-medium text-lg text-[#1a1a1a]">Start Building Free</span>
                <span className="w-10 h-10 rounded-full bg-[#3054ff] group-hover:bg-[#2040e0] flex items-center justify-center transition-colors">
                  <ArrowRight className="w-5 h-5 text-white" />
                </span>
              </motion.button>
            ) : (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.35, ease: EASE_CINEMATIC }}
                className="w-full space-y-6"
              >
                <PromptInputBox
                  autoFocus
                  onSend={handleSend}
                  placeholder="Example: I run a bakery in Brooklyn and I want a website where customers can see my menu and order online."
                />
                <Link
                  href="/migrate"
                  className="text-sm text-white/60 hover:text-white/90 inline-flex items-center gap-2 transition-colors"
                >
                  <span>Already have a site?</span>
                  <span className="font-semibold underline underline-offset-2">Bring it over →</span>
                </Link>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {mounted && resumeName && (
          <motion.button
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0, transition: { delay: 0.3, duration: SHORT_S, ease: EASE_CINEMATIC } }}
            onClick={handleResume}
            className="group flex items-center gap-2 px-5 py-3 bg-white/5 hover:bg-white/10 border border-white/15 rounded-full text-white/80 hover:text-white text-sm backdrop-blur-sm transition-colors"
          >
            <span>Continue working on</span>
            <span className="text-white font-medium">{resumeName}</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-0.5" />
          </motion.button>
        )}
        </motion.div>
      </section>

      {/* ════════════════════════════════════════════════════════════════
          LIGHT MARKETING BODY — white → soft gray gradient
          ════════════════════════════════════════════════════════════════ */}
      <div className="relative bg-gradient-to-b from-white via-white to-stone-100 text-[#1a1a1a]">
        {/* §2 — From sentence to site. */}
        <section
          id="how"
          ref={sentenceSec.ref}
          className="relative min-h-[75vh] flex flex-col justify-center px-4 max-w-6xl mx-auto py-16"
        >
          <motion.div
            style={{ y: sentenceSec.headingY, opacity: sentenceSec.opacity }}
            className="text-center mb-16 space-y-4 will-change-transform"
          >
            <h2 className={`text-4xl sm:text-6xl font-semibold tracking-tight ${lightGradient}`}>
              From sentence to site.
            </h2>
            <p className="text-lg text-[#1a1a1a]/65 max-w-xl mx-auto">
              Three steps from a paragraph about your business to a real, editable website.
            </p>
          </motion.div>

          <motion.div
            style={{ y: sentenceSec.bodyY, opacity: sentenceSec.opacity }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 will-change-transform"
          >
            {STEPS.map((step) => (
              <div key={step.title} className="p-8 rounded-2xl bg-white border border-stone-200">
                <step.Icon className="w-8 h-8 text-[#3054ff] mb-6" />
                <h3 className={`${type.heading.l} mb-3`}>{step.title}</h3>
                <p className="text-[#1a1a1a]/65 leading-relaxed">{step.body}</p>
              </div>
            ))}
          </motion.div>
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
            <h2 className={`text-4xl sm:text-6xl font-semibold tracking-tight ${lightGradient}`}>
              The looks Pebble can wear.
            </h2>
            <p className="text-lg text-[#1a1a1a]/65 max-w-2xl mx-auto">
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
                className="p-6 rounded-xl bg-white border border-stone-200 hover:border-[#3054ff]/40 transition-colors"
              >
                <h3 className={`${type.heading.s} mb-2`}>{dna.label}</h3>
                <p className="text-sm text-[#1a1a1a]/60 leading-relaxed">{dna.feel}</p>
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
            <h2 className={`text-4xl sm:text-6xl font-semibold tracking-tight ${lightGradient}`}>
              Perfect for…
            </h2>
            <p className="text-lg text-[#1a1a1a]/65 max-w-xl mx-auto">
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
                className="px-5 py-3 rounded-full bg-white border border-stone-200 text-[#1a1a1a]/85 text-sm sm:text-base"
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
            <p className={`font-[family-name:var(--font-instrument-serif)] italic text-3xl sm:text-4xl leading-[1.2] ${lightGradient}`}>
              &ldquo;We&apos;re building Pebble in public. A real testimonial from a real beta user will land here once their site is shipped. We&apos;d rather wait than make one up.&rdquo;
            </p>
            <footer className="text-sm text-[#1a1a1a]/55">— Pebble, May 2026</footer>
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
            <h2 className={`text-4xl sm:text-6xl font-semibold tracking-tight ${lightGradient}`}>
              Simple pricing.
            </h2>
            <p className="text-lg text-[#1a1a1a]/65 max-w-xl mx-auto">
              Start free. Upgrade when you need more sites or a custom domain.
            </p>

            {/* Billing toggle — animated thumb slides between Monthly / Yearly. */}
            <div className="inline-flex items-center gap-1 p-1 rounded-full bg-stone-200/70 border border-stone-200 mt-4">
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
                  <span className={`relative z-10 capitalize ${billing === opt ? "text-[#1a1a1a]" : "text-[#1a1a1a]/55"}`}>
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
                        ? "bg-white border-2 border-[#3054ff] shadow-[0_12px_32px_rgba(48,84,255,0.18)] lg:scale-[1.03] lg:-translate-y-2"
                        : "bg-white border border-stone-200"
                    }`}
                  >
                    {tier.featured && (
                      <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-[#3054ff] text-white text-[10px] font-semibold uppercase tracking-wider whitespace-nowrap">
                        Most popular
                      </div>
                    )}

                    <div className="text-xs uppercase tracking-wider text-[#1a1a1a]/55 mb-2">{tier.name}</div>

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
                          <span className="text-3xl font-semibold">{headlinePrice}</span>
                          {period && <span className="text-sm text-[#1a1a1a]/55">{period}</span>}
                        </motion.div>
                      </AnimatePresence>
                      <div className="text-xs text-[#1a1a1a]/45 mt-1 h-4">{subtext}</div>
                    </div>

                    <p className="text-sm text-[#1a1a1a]/70 leading-relaxed mb-5">{tier.desc}</p>

                    <ul className="space-y-2 text-sm text-[#1a1a1a]/75 mb-4 flex-1">
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
                      className="flex items-center justify-center gap-1.5 text-xs font-medium text-[#1a1a1a]/55 hover:text-[#1a1a1a] mb-4 transition-colors"
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
                          <div className="space-y-4 pt-2 pb-4 border-t border-stone-200">
                            {tier.details.map((cat) => (
                              <div key={cat.category}>
                                <div className="text-[10px] uppercase tracking-wider text-[#1a1a1a]/50 mb-2 mt-3">
                                  {cat.category}
                                </div>
                                <ul className="space-y-1.5 text-sm text-[#1a1a1a]/75">
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
                          ? "bg-stone-100 hover:bg-stone-200 text-[#1a1a1a]"
                          : tier.featured
                            ? "bg-[#3054ff] hover:bg-[#2040e0] text-white"
                            : "bg-stone-100 hover:bg-stone-200 text-[#1a1a1a]"
                      }`;

                      if (tier.ctaHref) {
                        return <a href={tier.ctaHref} className={buttonClass}>{label}</a>;
                      }
                      return (
                        <button
                          type="button"
                          onClick={() => handleChoosePlan(tier)}
                          disabled={isLoading}
                          className={buttonClass}
                        >
                          {label}
                        </button>
                      );
                    })()}
                  </div>
                );
              })}
            </div>

            {stripeError && (
              <p className="mt-4 text-center text-sm text-red-600">{stripeError}</p>
            )}
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
            <p className="text-sm uppercase tracking-wider text-[#1a1a1a]/55">Ready to build?</p>
            <h2 className={`text-4xl sm:text-6xl font-semibold tracking-tight leading-[1.05] ${lightGradient}`}>
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

            <p className="text-sm text-[#1a1a1a]/55">
              You&apos;ll see exactly what I&apos;m doing every step of the way. Nothing is final until you say it is.
            </p>
          </motion.div>
        </section>

        {/* §8 — Footer. */}
        <footer className="border-t border-stone-200 px-4 py-12">
          <div className="max-w-6xl mx-auto flex flex-col sm:flex-row justify-between gap-8">
            <div className="space-y-2">
              <Link href="/" className={`text-xl font-semibold ${lightGradient}`}>
                Pebble.
              </Link>
              <p className="text-sm text-[#1a1a1a]/55 max-w-xs">
                A website you understand, built with you, not just for you.
              </p>
            </div>
            <div className="grid grid-cols-3 gap-12 text-sm">
              <div className="space-y-3">
                <div className="text-[#1a1a1a]/45 uppercase tracking-wider text-xs">Product</div>
                <a href="#pricing" className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Pricing</a>
                <Link href="/help"    className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Help</Link>
              </div>
              <div className="space-y-3">
                <div className="text-[#1a1a1a]/45 uppercase tracking-wider text-xs">Legal</div>
                <Link href="/privacy" className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Privacy</Link>
                <Link href="/terms"   className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Terms</Link>
              </div>
              <div className="space-y-3">
                <div className="text-[#1a1a1a]/45 uppercase tracking-wider text-xs">Account</div>
                <Link href="/login"  className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Log in</Link>
                <Link href="/signup" className="block text-[#1a1a1a]/75 hover:text-[#1a1a1a]">Sign up</Link>
              </div>
            </div>
          </div>
          <div className="max-w-6xl mx-auto mt-12 pt-8 border-t border-stone-200/70 text-xs text-[#1a1a1a]/45">
            © 2026 Pebble. Made for people who want to actually understand their website.
          </div>
        </footer>
      </div>
    </div>
  );
}
