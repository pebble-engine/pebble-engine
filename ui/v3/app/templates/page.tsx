"use client";

/**
 * Templates Gallery — /templates
 *
 * Phase 31 (2026-05-20). The Webild-parity move: instead of asking every
 * customer to design from a blank prompt, surface a curated gallery of
 * designer-vetted starting points. Click → fill in business info →
 * 30-second content-swap LLM call → done. Free tier defaults to this
 * path because each instantiation costs ~$0.005 (vs $0.02-0.50 for
 * full /api/generate).
 *
 * The visual hook is "Templates Are Free" — copying Webild's exact
 * marketing framing because it works. The carrot routes lowest-commitment
 * users into the cheapest, most-likely-to-look-good path.
 */
import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, Check, X, Loader2, Eye, ExternalLink, Lock, Upload } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { type } from "@/lib/type";
import {
  listTemplates,
  instantiateTemplate,
  type TemplateSummary,
} from "@/lib/api";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC } from "@/lib/motion";
import { type Brief } from "@/lib/state";

// 2026-05-23: tier-tab model. Marc's design-night ask was three tabs —
// Free / Premium / Public — where Public is user-uploaded with a
// revenue split. The backend registry still emits some templates with
// the legacy tier="paid"; we treat that as "premium" client-side via
// `normalizeTier()` below, so the UI tabs don't depend on a backend
// rename.
type TierTab = "free" | "premium" | "public";

function normalizeTier(t: TemplateSummary["tier"]): TierTab {
  if (t === "paid" || t === "premium") return "premium";
  if (t === "public") return "public";
  return "free";
}

export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<TemplateSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Phase 32a (2026-05-20) — two-step flow: clicking a card opens the
  // PREVIEW pane (iframe + page tabs). User browses home/about/etc.
  // before clicking "Use this template" → instantiate dialog.
  const [previewing, setPreviewing] = useState<TemplateSummary | null>(null);
  const [picked, setPicked] = useState<TemplateSummary | null>(null);
  const [activeTab, setActiveTab] = useState<TierTab>("free");

  useEffect(() => {
    listTemplates()
      .then((res) => setTemplates(res.templates))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  // Pre-bucket once per templates load so the tab counters + filtered
  // list don't recompute every keystroke.
  const buckets = useMemo(() => {
    const out: Record<TierTab, TemplateSummary[]> = { free: [], premium: [], public: [] };
    (templates ?? []).forEach((t) => out[normalizeTier(t.tier)].push(t));
    return out;
  }, [templates]);

  const visible = buckets[activeTab];

  return (
    <div className="min-h-screen-safe flex flex-col bg-background text-foreground">
      <TopNav />
      <main className="flex-1 px-6 md:px-12 lg:px-16 py-12 max-w-7xl mx-auto w-full">
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full border border-border bg-card text-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span className={`${type.mono} uppercase tracking-wider`}>Templates are free</span>
          </div>
          <h1 className={`${type.dashboard.display.l} mb-3`}>Start with a template</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-2xl mx-auto`}>
            Hand-curated designs across industries. Tell us your business and we build you a
            <strong className="text-foreground font-medium"> custom version in about 30 seconds</strong> —
            then customize anything.
          </p>
          <p className={`${type.body.s} text-muted-foreground mt-3`}>
            Just want to start instantly?{" "}
            <Link href="/examples" className="text-foreground underline underline-offset-2 hover:opacity-80">
              Copy a finished site from Examples →
            </Link>
          </p>
        </header>

        {error && (
          <div className="max-w-md mx-auto p-4 rounded-lg border border-red-300 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
            Couldn't load templates: {error}
          </div>
        )}

        {!templates && !error && (
          <div className="text-center text-muted-foreground py-16">
            <Loader2 className="w-6 h-6 mx-auto mb-3 animate-spin" />
            <p className={type.body.s}>Loading the gallery…</p>
          </div>
        )}

        {/* Tier tabs — Free / Premium / Public. Counts reflect what's
            actually in each bucket; Public is intentionally empty today
            (marketplace upload flow not yet built) and renders a
            dedicated "coming soon + waitlist" panel rather than an
            empty grid. Marc's 2026-05-23 brief: Public templates are
            user-uploaded with a revenue split. */}
        {templates && (
          <div className="flex items-center justify-center gap-1.5 mb-8">
            <TierTabButton
              active={activeTab === "free"}
              count={buckets.free.length}
              onClick={() => setActiveTab("free")}
            >
              Free
            </TierTabButton>
            <TierTabButton
              active={activeTab === "premium"}
              count={buckets.premium.length}
              onClick={() => setActiveTab("premium")}
            >
              Premium
            </TierTabButton>
            <TierTabButton
              active={activeTab === "public"}
              count={buckets.public.length}
              onClick={() => setActiveTab("public")}
            >
              Public
            </TierTabButton>
          </div>
        )}

        {/* Empty states + grid per tab */}
        {templates && activeTab === "public" && buckets.public.length === 0 && (
          <PublicTabPlaceholder />
        )}

        {templates && activeTab === "premium" && buckets.premium.length === 0 && (
          <div className="text-center text-muted-foreground py-16 max-w-md mx-auto">
            <Lock className="w-6 h-6 mx-auto mb-3 opacity-40" />
            <p className={`${type.dashboard.heading.m} text-foreground mb-1`}>No premium templates yet</p>
            <p className={type.body.s}>
              Pebble-curated paid templates are coming. For now, every Free template ships ready to customize.
            </p>
          </div>
        )}

        {templates && activeTab === "free" && buckets.free.length === 0 && (
          <div className="text-center text-muted-foreground py-16">
            <p className={type.body.m}>No templates available yet.</p>
          </div>
        )}

        {templates && visible.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {visible.map((t, i) => (
              <TemplateCard
                key={t.id}
                template={t}
                index={i}
                onClick={() => setPreviewing(t)}
              />
            ))}
          </div>
        )}
      </main>
      {previewing && (
        <PreviewPane
          template={previewing}
          allTemplates={templates ?? []}
          onClose={() => setPreviewing(null)}
          onUseTemplate={(t) => {
            setPreviewing(null);
            setPicked(t);
          }}
        />
      )}
      {picked && <InstantiateDialog template={picked} onClose={() => setPicked(null)} router={router} />}
    </div>
  );
}

// ------------------------------------------------------------------ //
// Template card — image OR fallback, never both                       //
// ------------------------------------------------------------------ //
// Phase 32e (2026-05-20). Earlier card had the fallback name overlay
// rendering on TOP of every working image via `mix-blend-overlay`,
// which made every card read as "big white serif name on a colored
// background" regardless of the screenshot underneath — the dominant
// homogenizing factor in the gallery. Fix: render fallback ONLY when
// no preview_image is set OR the image fails to load (error state).

function TemplateCard({
  template: t,
  index: i,
  onClick,
}: {
  template: TemplateSummary;
  index: number;
  onClick: () => void;
}) {
  const [imgErrored, setImgErrored] = useState(false);
  const showFallback = !t.preview_image || imgErrored;
  return (
    <motion.button
      onClick={onClick}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: STANDARD_S, delay: i * 0.05, ease: EASE_CINEMATIC }}
      className="group text-left bg-card border border-border rounded-2xl overflow-hidden hover:border-foreground/30 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
    >
      <div
        className="relative aspect-[4/3] w-full overflow-hidden bg-muted"
        style={{
          background: showFallback && t.color_swatches?.length
            ? `linear-gradient(135deg, ${t.color_swatches.join(", ")})`
            : undefined,
        }}
      >
        {!showFallback && (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={t.preview_image}
            alt={`${t.name} preview`}
            className="absolute inset-0 w-full h-full object-cover object-top"
            loading="lazy"
            onError={() => setImgErrored(true)}
          />
        )}
        {showFallback && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <p
              className={`${type.dashboard.display.m} opacity-90 px-4 text-center`}
              style={{
                fontFamily: t.fonts?.display
                  ? `'${t.fonts.display}', serif`
                  : undefined,
              }}
            >
              {t.name}
            </p>
          </div>
        )}
        {/* Tier badge — top-left. "Pro" for premium templates so users
            read it as a plan-gate signal, not a price tag. Free stays Free. */}
        <div className={`absolute top-3 left-3 px-2.5 py-0.5 rounded-full text-xs uppercase tracking-wider z-10 ${
          normalizeTier(t.tier) === "premium"
            ? "bg-violet-600/95 text-white"
            : normalizeTier(t.tier) === "public"
              ? "bg-emerald-600/95 text-white"
              : "bg-foreground/85 text-background"
        }`}>
          {(() => {
            const tier = normalizeTier(t.tier);
            if (tier === "free") return "Free";
            if (tier === "premium") return "Pro";
            return "Public";
          })()}
        </div>
        {/* Lock overlay on premium — visual cue that this needs a paid plan.
            Tap-through still opens the preview; the InstantiateDialog gates
            on actual subscription server-side. */}
        {normalizeTier(t.tier) === "premium" && (
          <div className="absolute top-3 right-3 z-10 inline-flex items-center justify-center w-7 h-7 rounded-full bg-violet-600/95 text-white shadow-lg">
            <Lock className="w-3.5 h-3.5" aria-hidden />
          </div>
        )}
      </div>
      {/* Simplified body — name + tagline + ≤2 industries.
          Marc 2026-05-24: dropped the vibe codename ("GLOW EMERALD DUAL-THEME")
          and reduced visible industries from 4 to 2 — the cards were reading
          as walls of tag chips. Names should carry the gallery, not metadata. */}
      <div className="p-5">
        <h3 className={`${type.dashboard.heading.m} mb-2`}>{t.name}</h3>
        <p className={`${type.body.s} text-muted-foreground line-clamp-1 mb-3`}>
          {t.tagline}
        </p>
        <div className="flex flex-wrap gap-1.5">
          {t.applicable_industries.slice(0, 2).map((ind) => (
            <span
              key={ind}
              className={`${type.mono} px-2 py-0.5 rounded-full bg-muted text-xs text-muted-foreground`}
            >
              {ind}
            </span>
          ))}
          {t.applicable_industries.length > 2 && (
            <span className={`${type.mono} px-2 py-0.5 rounded-full text-xs text-muted-foreground`}>
              +{t.applicable_industries.length - 2}
            </span>
          )}
        </div>
      </div>
    </motion.button>
  );
}

// ------------------------------------------------------------------ //
// Template family helper — groups base + all its color variants       //
// ------------------------------------------------------------------ //
// A "family" is the base template + every variant whose id starts
// with "{base_id}_". Bases are identified by having a `preview_url`.

function getFamily(
  template: TemplateSummary,
  all: TemplateSummary[],
): TemplateSummary[] {
  const baseId = template.preview_url
    ? template.id
    : (all.find((t) => t.preview_url && template.id.startsWith(t.id + "_"))?.id ?? "");
  if (!baseId) return [template];
  return all.filter((t) => t.id === baseId || t.id.startsWith(baseId + "_"));
}

// ------------------------------------------------------------------ //
// Preview pane (Phase 32e) — screenshot/iframe + variant strip + auth //
// ------------------------------------------------------------------ //
// All 21 cards now open this pane. For base templates it shows the
// live iframe (with page tabs). For color variants it shows the
// Playwright screenshot. Either way the family variant strip lets users
// browse siblings before committing. "Want to use this template?" is
// auth-gated: anonymous users see a soft sign-in nudge rather than a
// hard redirect.

function PreviewPane({
  template: initialTemplate,
  allTemplates,
  onClose,
  onUseTemplate,
}: {
  template: TemplateSummary;
  allTemplates: TemplateSummary[];
  onClose: () => void;
  onUseTemplate: (t: TemplateSummary) => void;
}) {
  const [current, setCurrent] = useState(initialTemplate);
  const [needsAuth, setNeedsAuth] = useState(false);
  const [checkingAuth, setCheckingAuth] = useState(false);
  const [activeIdx, setActiveIdx] = useState(0);

  // Esc closes the preview — standard modal UX (backdrop-click already works).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const family = getFamily(initialTemplate, allTemplates);
  const pages =
    current.preview_pages && current.preview_pages.length > 0
      ? current.preview_pages
      : [{ label: "Home", path: "/" }];

  // Reset page tab + auth nudge when the user switches variants
  useEffect(() => {
    setActiveIdx(0);
    setNeedsAuth(false);
  }, [current.id]);

  const active = pages[activeIdx] ?? pages[0];
  // Templates with absolute preview_urls (legacy localhost:3199 entries) load
  // as-is. Engine-served static-export URLs (/preview-template/<id>/...) need
  // the engine origin prefixed so the iframe resolves to port 8000, not v3's
  // port 3001. Mirror the ENGINE_BASE logic from lib/api.ts exactly.
  const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
  const previewUrl = current.preview_url ?? "";
  // Both preview_url and active.path may carry a leading/trailing slash —
  // naive concat ("/preview-template/<id>/" + "/about") emits a double slash
  // that the engine's path-traversal guard interprets as an absolute path
  // and 403s ("path outside template root"). Normalize once here.
  const trimmedPath = (active.path || "").replace(/^\/+/, "");
  const trimmedPreview = previewUrl.replace(/\/+$/, "");
  const iframeSrc = previewUrl.startsWith("/")
    ? `${ENGINE_BASE}${trimmedPreview}/${trimmedPath}`
    : `${trimmedPreview}/${trimmedPath}`;

  const handleUseTemplate = async () => {
    setCheckingAuth(true);
    try {
      const { createClient } = await import("@/lib/supabase/client");
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        setNeedsAuth(true);
        return;
      }
      onUseTemplate(current);
    } finally {
      setCheckingAuth(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/85 flex flex-col" onClick={onClose}>
      {/* ── Header bar ── */}
      <div
        className="flex items-center justify-between gap-3 px-6 py-3 border-b border-white/10 bg-black"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 min-w-0">
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-md text-white/70 hover:bg-white/10 hover:text-white shrink-0"
            aria-label="Close preview"
          >
            <X className="w-5 h-5" />
          </button>
          <div className="min-w-0">
            {/* Vibe codename (e.g. "glow-emerald-dual-theme") is internal
                metadata — dropped from the header so users see the template
                NAME, not jargon. Matches the card decision (2026-05-24). */}
            <h2 className={`${type.dashboard.heading.m} text-white truncate`}>{current.name}</h2>
          </div>
        </div>

        {/* Page tabs — only shown when a live iframe is available */}
        {current.preview_url && (
          <div className="flex items-center gap-1 overflow-x-auto">
            {pages.map((p, i) => (
              <button
                key={p.label}
                type="button"
                onClick={() => setActiveIdx(i)}
                className={`${type.label} px-3 py-1.5 rounded-md transition-colors shrink-0 ${
                  i === activeIdx
                    ? "bg-white text-black"
                    : "text-white/70 hover:bg-white/10 hover:text-white"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 shrink-0">
          {current.preview_url && (
            <a
              href={iframeSrc}
              target="_blank"
              rel="noopener noreferrer"
              title="Open in new tab"
              className="p-1.5 rounded-md text-white/70 hover:bg-white/10 hover:text-white"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
          <button
            type="button"
            onClick={handleUseTemplate}
            disabled={checkingAuth}
            className="px-4 py-2 rounded-full bg-white text-black font-medium text-sm hover:bg-white/90 disabled:opacity-60 flex items-center gap-2"
          >
            {checkingAuth && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            Want to use this template?
          </button>
        </div>
      </div>

      {/* ── Color-variant family strip ── */}
      {family.length > 1 && (
        <div
          className="flex items-center gap-2 px-6 py-2.5 border-b border-white/10 bg-black/80 overflow-x-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <span
            className={`${type.mono} text-[10px] uppercase tracking-wider text-white/40 shrink-0 mr-1`}
          >
            Color variants
          </span>
          {family.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setCurrent(t)}
              title={t.name}
              className={`relative shrink-0 w-10 h-10 rounded-lg overflow-hidden border-2 transition-all ${
                t.id === current.id
                  ? "border-white scale-110"
                  : "border-transparent opacity-50 hover:opacity-90"
              }`}
              style={{
                background: t.color_swatches?.length
                  ? `linear-gradient(135deg, ${t.color_swatches.slice(0, 3).join(", ")})`
                  : "#222",
              }}
            >
              {t.preview_image && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={t.preview_image}
                  alt={t.name}
                  className="absolute inset-0 w-full h-full object-cover object-top"
                />
              )}
            </button>
          ))}
        </div>
      )}

      {/* ── Auth nudge (shown when session check fails) ── */}
      {needsAuth && (
        <div
          className="flex items-center justify-between gap-3 px-6 py-3 bg-amber-950/80 border-b border-amber-800/50"
          onClick={(e) => e.stopPropagation()}
        >
          <p className="text-amber-200 text-sm">
            Sign in first — it only takes a moment, and your template choice is saved.
          </p>
          <a
            href="/login?next=/templates"
            className="px-4 py-1.5 rounded-full bg-white text-black text-sm font-medium hover:bg-white/90 shrink-0"
          >
            Sign in →
          </a>
        </div>
      )}

      {/* ── Preview area ── */}
      <div className="flex-1 p-6" onClick={(e) => e.stopPropagation()}>
        {current.preview_url ? (
          <iframe
            key={iframeSrc}
            src={iframeSrc}
            className="w-full h-full rounded-lg border border-white/10 bg-white"
            title={`${current.name} ${active.label} preview`}
            // allow-downloads is required because Next.js static export
            // (basePath: "/preview-template/<id>") triggers a "download"
            // sandbox check on font preload / image-asset prefetches that
            // get classified as attachments by Chrome's heuristic. Without
            // it the iframe body stays empty even when the engine returns 200.
            // allow-popups + allow-popups-to-escape-sandbox so target=_blank
            // links from inside the preview (e.g. "View live") open properly.
            sandbox="allow-scripts allow-same-origin allow-forms allow-downloads allow-popups allow-popups-to-escape-sandbox"
          />
        ) : current.preview_image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={current.preview_image}
            alt={`${current.name} preview`}
            className="w-full h-full object-contain object-top rounded-lg border border-white/10"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center rounded-lg border border-white/10 bg-black/60">
            <div className="text-center text-white/70">
              <Eye className="w-8 h-8 mx-auto mb-3 opacity-40" />
              <p className={`${type.body.s}`}>Preview not available for this template yet.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ------------------------------------------------------------------ //
// Instantiate dialog — minimal business-info form + content-swap call //
// ------------------------------------------------------------------ //

function InstantiateDialog({
  template,
  onClose,
  router,
}: {
  template: TemplateSummary;
  onClose: () => void;
  router: ReturnType<typeof useRouter>;
}) {
  const [businessName, setBusinessName] = useState("");
  const [businessType, setBusinessType] = useState(
    template.applicable_industries[0] || "",
  );
  const [location, setLocation] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Esc closes the dialog — standard modal UX.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const submit = async () => {
    if (!businessName.trim()) {
      setError("Please give your business a name");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const brief: Brief = {
        business_name: businessName.trim(),
        business_type: businessType.trim(),
        location: location.trim(),
        notes_freeform: notes.trim(),
      };
      const res = await instantiateTemplate(template.id, brief);
      if (!res.ok || !res.slug) {
        throw new Error(res.swap_message || "Template instantiation failed");
      }
      router.push(`/workspace/${encodeURIComponent(res.slug)}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.96, y: 8 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: SHORT_S, ease: EASE_CINEMATIC }}
        className="w-full max-w-lg bg-card border border-border rounded-2xl p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <p className={`${type.mono} text-xs uppercase tracking-wider text-muted-foreground mb-1`}>
              {template.vibe}
            </p>
            <h2 className={`${type.dashboard.heading.l}`}>Use {template.name}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-md text-muted-foreground hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <p className={`${type.body.s} text-muted-foreground mb-5`}>{template.best_for}</p>

        <div className="space-y-4">
          <FieldLabel label="Your business name" required>
            <input
              type="text"
              value={businessName}
              onChange={(e) => setBusinessName(e.target.value)}
              placeholder="e.g. Coastal Pro Services"
              className="w-full px-3 py-2 rounded-md bg-background border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
              autoFocus
            />
          </FieldLabel>
          <FieldLabel label="Industry">
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-background border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
            >
              {template.applicable_industries.map((ind) => (
                <option key={ind} value={ind}>
                  {ind}
                </option>
              ))}
            </select>
          </FieldLabel>
          <FieldLabel label="Where you serve (optional)">
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. Long Island, NY"
              className="w-full px-3 py-2 rounded-md bg-background border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
            />
          </FieldLabel>
          <FieldLabel label="Anything else? (optional)">
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What you offer, what makes you different, key services…"
              rows={3}
              className="w-full px-3 py-2 rounded-md bg-background border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60 resize-none"
            />
          </FieldLabel>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-md bg-red-50 dark:bg-red-950 border border-red-300 dark:border-red-900 text-red-900 dark:text-red-200 text-sm">
            {error}
          </div>
        )}

        <div className="mt-6 flex items-center justify-between">
          <p className={`${type.mono} text-xs text-muted-foreground`}>
            <Check className="inline w-3.5 h-3.5 mr-1 text-foreground" />
            Free · takes ~30 seconds to build · customize after.
          </p>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="px-5 py-2 rounded-full bg-foreground text-background font-medium hover:bg-foreground/90 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60 transition-colors flex items-center gap-2"
          >
            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
            {submitting ? "Building your version…" : "Build my version"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function FieldLabel({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className={`${type.label} block mb-1.5`}>
        {label}
        {required && <span className="text-red-500 ml-0.5">*</span>}
      </span>
      {children}
    </label>
  );
}

// ------------------------------------------------------------------ //
// Tier tab + Public placeholder (2026-05-23)                          //
// ------------------------------------------------------------------ //

function TierTabButton({
  active, count, onClick, children,
}: {
  active: boolean;
  count: number;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
        active
          ? "bg-foreground text-background"
          : "bg-card border border-border text-muted-foreground hover:text-foreground"
      }`}
    >
      <span>{children}</span>
      <span
        className={`inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[10px] font-bold ${
          active ? "bg-background/20 text-background" : "bg-muted text-muted-foreground"
        }`}
      >
        {count}
      </span>
    </button>
  );
}

// Public tab: when the marketplace ships (user uploads + revenue split),
// this placeholder gets replaced with a real listing + an upload CTA.
// Until then we surface the value prop + capture interest so users know
// it's coming and we don't leave an empty grid feeling broken.
function PublicTabPlaceholder() {
  // 2026-05-24: rewritten from passive "coming soon" → 3 active creator
  // CTAs. Marc wanted this section to invite community contributions
  // instead of advertising vaporware. Each CTA hits a different intent
  // (ready-now / idea-stage / total-newcomer) so no one falls through.
  return (
    <section className="max-w-3xl mx-auto">
      <div className="rounded-2xl border border-border bg-card p-8 md:p-10 text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 mb-4">
          <Upload className="w-5 h-5 text-primary" />
        </div>
        <h2 className={`${type.dashboard.display.m} text-foreground mb-2`}>
          Built something? Show the community.
        </h2>
        <p className={`${type.body.m} text-muted-foreground mb-8 max-w-xl mx-auto`}>
          Pebble&apos;s catalog is open to designers, agencies, and builders. Ship a finished template,
          pitch us an idea, or just start designing in our framework — every contributor gets credit
          on every install.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
          {/* CTA 1 — ready-now: full template upload */}
          <a
            href="mailto:hello@getpebble.net?subject=Pebble%20—%20I%20want%20to%20submit%20a%20template&body=Tell%20us%20about%20your%20template%3A%20industry%2C%20design%20vibe%2C%20link%20to%20a%20live%20demo%20or%20Figma%20file."
            className="group rounded-xl border border-border bg-background p-5 hover:border-primary/60 hover:bg-card transition-colors flex flex-col"
          >
            <p className={`${type.mono} text-xs uppercase tracking-wider text-primary mb-2`}>
              Submit a template
            </p>
            <p className={`${type.body.s} text-foreground mb-auto`}>
              Already have a finished design? Send us the live URL or Figma file.
              Approved templates ship with your credit and a revenue share.
            </p>
            <span className="text-xs font-semibold text-primary mt-3 group-hover:underline">
              Open contact →
            </span>
          </a>

          {/* CTA 2 — idea-stage: pitch / collaborate */}
          <a
            href="mailto:hello@getpebble.net?subject=Pebble%20—%20Template%20idea&body=My%20industry%20%2F%20idea%3A%0A%0AWhat%20it%20should%20feel%20like%3A%0A%0AReferences%20%2F%20inspiration%3A"
            className="group rounded-xl border border-border bg-background p-5 hover:border-primary/60 hover:bg-card transition-colors flex flex-col"
          >
            <p className={`${type.mono} text-xs uppercase tracking-wider text-primary mb-2`}>
              Share an idea
            </p>
            <p className={`${type.body.s} text-foreground mb-auto`}>
              Have a template idea but no time to build it? Tell us the industry + vibe.
              We&apos;ll build it and credit you as the originator.
            </p>
            <span className="text-xs font-semibold text-primary mt-3 group-hover:underline">
              Pitch us →
            </span>
          </a>

          {/* CTA 3 — total newcomer: get started */}
          <a
            href="/community/launchpad"
            className="group rounded-xl border border-border bg-background p-5 hover:border-primary/60 hover:bg-card transition-colors flex flex-col"
          >
            <p className={`${type.mono} text-xs uppercase tracking-wider text-primary mb-2`}>
              Get started
            </p>
            <p className={`${type.body.s} text-foreground mb-auto`}>
              New to designing for Pebble? Start here — quick docs on our template system,
              the DNA model, and how the engine renders your work.
            </p>
            <span className="text-xs font-semibold text-primary mt-3 group-hover:underline">
              Open Launchpad →
            </span>
          </a>
        </div>

        <p className={`${type.mono} text-xs text-muted-foreground mt-8`}>
          Every approved contributor earns 30% of every install of their template, recurring.
        </p>
      </div>
    </section>
  );
}
