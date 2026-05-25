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
 * Phase 56a (2026-05-25): Rebuilt as a cinematic horizontal carousel.
 * B&W full-bleed slides, uppercase serif headline overlays, thumbnail
 * ribbon replaces chip filter row.
 */
import { useCallback, useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Check, X, Loader2, Eye, ExternalLink, Upload } from "lucide-react";
import { FloatingPeblet } from "@/components/floating-peblet";
import { TopNav } from "@/components/top-nav";
import { type } from "@/lib/type";
import {
  listTemplates,
  instantiateTemplate,
  type TemplateSummary,
} from "@/lib/api";
import { SHORT_S, EASE_CINEMATIC } from "@/lib/motion";
import { type Brief } from "@/lib/state";


export default function TemplatesPage() {
  const router = useRouter();
  const [templates, setTemplates] = useState<TemplateSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [previewing, setPreviewing] = useState<TemplateSummary | null>(null);
  const [picked, setPicked] = useState<TemplateSummary | null>(null);
  const [activeIndustry, setActiveIndustry] = useState<string | null>(null);
  const [carouselIndex, setCarouselIndex] = useState(0);

  useEffect(() => {
    listTemplates()
      .then((res) => setTemplates(res.templates))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  // Reset to start when filter changes
  useEffect(() => {
    setCarouselIndex(0);
  }, [activeIndustry]);

  // Unique sorted industry list extracted from all templates.
  const industries = useMemo(() => {
    const seen = new Set<string>();
    (templates ?? []).forEach((t) =>
      t.applicable_industries.forEach((i) => seen.add(i)),
    );
    return Array.from(seen).sort();
  }, [templates]);

  // Helper: first color_swatches array for a given industry.
  const firstSwatchForIndustry = useCallback(
    (ind: string): string[] | null => {
      const t = (templates ?? []).find((x) => x.applicable_industries.includes(ind));
      return t?.color_swatches?.length ? t.color_swatches : null;
    },
    [templates],
  );

  // Helper: first preview_image for a given industry (thumbnail ribbon)
  const firstImageForIndustry = useCallback(
    (ind: string): string | null => {
      const t = (templates ?? []).find((x) => x.applicable_industries.includes(ind));
      return t?.preview_image ?? null;
    },
    [templates],
  );

  const visible = useMemo(
    () =>
      (templates ?? []).filter(
        (t) => !activeIndustry || t.applicable_industries.includes(activeIndustry),
      ),
    [templates, activeIndustry],
  );

  return (
    <div className="min-h-screen-safe flex flex-col bg-background text-foreground">
      <TopNav />
      <main className="flex-1 px-6 md:px-12 lg:px-16 py-12 max-w-7xl mx-auto w-full">
        {/* ── Page header ── */}
        <header className="text-center mb-12">
          <p className={`${type.mono} text-[10px] uppercase tracking-widest text-muted-foreground mb-3`}>
            Template gallery
          </p>
          <h1 className={`${type.dashboard.display.l} mb-3`}>Cinematic Template Carousel</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-2xl mx-auto`}>
            Curated for professionals. Build with confidence.
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

        {/* Template grid — filtered by active industry */}
        {templates && visible.length === 0 && (
          <div className="text-center text-muted-foreground py-16">
            <p className={type.body.m}>No templates for that industry yet.</p>
          </div>
        )}

        {/* ── Cinematic carousel ── */}
        {templates && visible.length > 0 && (
          <div className="relative mb-10">
            {/* Prev chevron */}
            <button
              type="button"
              onClick={() => setCarouselIndex((i) => Math.max(0, i - 1))}
              disabled={carouselIndex === 0}
              aria-label="Previous template"
              className="absolute left-2 md:left-4 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-white/90 text-black hover:bg-white flex items-center justify-center shadow-xl disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            {/* Next chevron */}
            <button
              type="button"
              onClick={() =>
                setCarouselIndex((i) => Math.min(visible.length - 1, i + 1))
              }
              disabled={carouselIndex >= visible.length - 1}
              aria-label="Next template"
              className="absolute right-2 md:right-4 top-1/2 -translate-y-1/2 z-20 w-11 h-11 rounded-full bg-white/90 text-black hover:bg-white flex items-center justify-center shadow-xl disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
            {/* Track */}
            <div className="overflow-hidden px-12">
              <motion.div
                className="flex gap-4 items-center"
                animate={{ x: -carouselIndex * 436 }}
                transition={{ duration: 0.55, ease: EASE_CINEMATIC }}
                style={{ paddingLeft: "calc(50% - 218px - 24px)" }}
              >
                {visible.map((t, i) => (
                  <CinematicSlide
                    key={t.id}
                    template={t}
                    active={i === carouselIndex}
                    onClick={() => setPreviewing(t)}
                  />
                ))}
              </motion.div>
            </div>
          </div>
        )}

        {/* ── Thumbnail Ribbon ── */}
        {templates && (
          <div className="space-y-3 mb-12">
            <p className={`${type.mono} text-[10px] uppercase tracking-widest text-muted-foreground text-center`}>
              Thumbnail ribbon
            </p>
            <div className="relative">
              <div aria-hidden="true" className="absolute left-0 top-0 bottom-0 w-12 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
              <div aria-hidden="true" className="absolute right-0 top-0 bottom-0 w-12 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
              <div className="flex gap-2 overflow-x-auto [&::-webkit-scrollbar]:hidden px-12 py-1">
                <ThumbnailRibbonChip
                  label="All"
                  imageSrc={null}
                  active={!activeIndustry}
                  onClick={() => setActiveIndustry(null)}
                />
                {industries.map((ind) => (
                  <ThumbnailRibbonChip
                    key={ind}
                    label={ind}
                    imageSrc={firstImageForIndustry(ind)}
                    active={activeIndustry === ind}
                    onClick={() => setActiveIndustry(ind)}
                  />
                ))}
                <SubmitThumbnail />
              </div>
            </div>
          </div>
        )}

        {/* ── Community Designs — user-submitted sites ──
            Until a real community submissions backend ships, the strip
            illustrates the section using a slice of the curated template
            previews so customers see what the format looks like. The
            "Submit yours" CTA routes to /community/launchpad which is
            already the submission entry point. */}
        {templates && templates.length > 0 && (
          <section className="space-y-4 mb-16">
            <div className="flex items-end justify-between gap-3 flex-wrap">
              <div>
                <h2 className={`${type.dashboard.heading.m}`}>Community Designs</h2>
                <p className={`${type.body.s} text-muted-foreground mt-1`}>
                  Sites built by Pebble users. Steal the structure, swap in your story.
                </p>
              </div>
              <Link
                href="/community/launchpad"
                className={`${type.label} text-primary inline-flex items-center gap-1 hover:underline`}
              >
                Submit yours <Upload className="w-3.5 h-3.5" />
              </Link>
            </div>
            <div className="relative">
              <div aria-hidden="true" className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
              <div aria-hidden="true" className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
              <div className="flex gap-3 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-2 snap-x">
                {templates.slice(0, 8).map((t) => (
                  <button
                    key={`community-${t.id}`}
                    type="button"
                    onClick={() => setPreviewing(t)}
                    aria-label={`Preview ${t.name}`}
                    className="group relative shrink-0 snap-start w-[180px] aspect-[4/3] rounded-lg overflow-hidden border border-border bg-card hover:border-foreground/40 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
                  >
                    {t.preview_image && (
                      /* eslint-disable-next-line @next/next/no-img-element */
                      <img
                        src={t.preview_image}
                        alt=""
                        aria-hidden="true"
                        className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
                        loading="lazy"
                      />
                    )}
                    <div className="absolute inset-x-0 bottom-0 p-2.5 bg-gradient-to-t from-black/85 via-black/30 to-transparent">
                      <p className="text-white text-xs font-semibold truncate">{t.name}</p>
                      <p className="text-white/60 text-[9px] uppercase tracking-widest truncate">
                        {t.applicable_industries[0] || "Community"}
                      </p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </section>
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
      <FloatingPeblet greeting="Looking for a template? I can help you find the right one." />
    </div>
  );
}

// ------------------------------------------------------------------ //
// CinematicSlide — B&W full-bleed with uppercase serif headline       //
// ------------------------------------------------------------------ //

function CinematicSlide({
  template: t,
  active,
  onClick,
}: {
  template: TemplateSummary;
  active: boolean;
  onClick: () => void;
}) {
  const [imgErrored, setImgErrored] = useState(false);
  const showFallback = !t.preview_image || imgErrored;
  // Tagline → uppercase. Strip punctuation softening so it reads bold.
  const headline = (t.tagline || t.name).toUpperCase();
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={`Preview ${t.name}`}
      className={`relative shrink-0 w-[300px] sm:w-[360px] md:w-[420px] aspect-[3/4] rounded-2xl overflow-hidden group transition-all duration-500 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60 ${
        active ? "scale-100 opacity-100" : "scale-[0.92] opacity-50"
      }`}
    >
      {/* Background image — grayscale by default, full color on hover */}
      {!showFallback && (
        /* eslint-disable-next-line @next/next/no-img-element */
        <img
          src={t.preview_image}
          alt=""
          aria-hidden="true"
          className="absolute inset-0 w-full h-full object-cover object-center grayscale group-hover:grayscale-0 transition-all duration-700"
          loading="lazy"
          onError={() => setImgErrored(true)}
        />
      )}
      {showFallback && (
        <div
          className="absolute inset-0"
          style={{
            background: t.color_swatches?.length
              ? `linear-gradient(135deg, ${t.color_swatches.join(", ")})`
              : "linear-gradient(135deg, #1a1a1a, #333)",
            filter: "grayscale(1)",
          }}
        />
      )}
      {/* Dark gradient overlay for text legibility */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent" />
      {/* Headline text — bottom-left aligned, scaled down for breathing room */}
      <div className="absolute inset-x-0 bottom-0 p-4 md:p-5 text-left">
        <h3
          className="text-white font-bold leading-[1.05] tracking-tight uppercase mb-1.5 line-clamp-3"
          style={{
            fontFamily: "Georgia, 'Times New Roman', serif",
            fontSize: "clamp(0.9rem, 1.2vw, 1.15rem)",
          }}
        >
          {headline}
        </h3>
        <p className="text-white/60 text-[9px] uppercase tracking-widest font-medium">
          {t.applicable_industries.slice(0, 2).join(" · ")}
        </p>
      </div>
    </button>
  );
}

// ------------------------------------------------------------------ //
// ThumbnailRibbonChip — small image card for industry filter          //
// ------------------------------------------------------------------ //

function ThumbnailRibbonChip({
  label,
  imageSrc,
  active,
  onClick,
}: {
  label: string;
  imageSrc?: string | null;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`relative shrink-0 w-[120px] h-[80px] rounded-lg overflow-hidden group transition-all border-2 ${
        active
          ? "border-foreground scale-100 opacity-100"
          : "border-transparent opacity-60 hover:opacity-100"
      }`}
      aria-label={`Filter by ${label}`}
      aria-pressed={active}
    >
      {imageSrc ? (
        /* eslint-disable-next-line @next/next/no-img-element */
        <img
          src={imageSrc}
          alt=""
          aria-hidden="true"
          className="absolute inset-0 w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all"
          loading="lazy"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-foreground/10 to-foreground/30" />
      )}
      <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors" />
      <span className="absolute inset-x-0 bottom-1 text-center text-white text-[9px] uppercase tracking-widest font-bold px-1 truncate">
        {label}
      </span>
    </button>
  );
}

// ------------------------------------------------------------------ //
// SubmitThumbnail — thumbnail-sized "Submit a template" CTA           //
// ------------------------------------------------------------------ //

function SubmitThumbnail() {
  return (
    <Link
      href="/community/launchpad"
      className="relative shrink-0 w-[120px] h-[80px] rounded-lg overflow-hidden border-2 border-dashed border-border bg-card hover:border-foreground transition-colors group flex flex-col items-center justify-center gap-1"
    >
      <Upload className="w-4 h-4 text-muted-foreground group-hover:text-foreground transition-colors" />
      <span className={`${type.mono} text-[9px] uppercase tracking-widest text-muted-foreground group-hover:text-foreground transition-colors`}>
        Submit
      </span>
    </Link>
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

  // Escape key closes the pane for keyboard users.
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const active = pages[activeIdx] ?? pages[0];
  const ENGINE_BASE = (process.env.NEXT_PUBLIC_PEBBLE_ENGINE_URL || "").replace(/\/+$/, "");
  const previewUrl = current.preview_url ?? "";
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
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="preview-pane-title"
      className="fixed inset-0 z-50 bg-black/85 flex flex-col"
      onClick={onClose}
    >
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
            <p className={`${type.mono} text-[10px] uppercase tracking-wider text-white/50`}>
              {current.vibe}
            </p>
            <h2 id="preview-pane-title" className={`${type.dashboard.heading.m} text-white truncate`}>{current.name}</h2>
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
              aria-label="Open preview in new tab"
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

  // Escape key closes the dialog for keyboard users.
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
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
      role="dialog"
      aria-modal="true"
      aria-labelledby="instantiate-dialog-title"
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
            <h2 id="instantiate-dialog-title" className={`${type.dashboard.heading.l}`}>Use {template.name}</h2>
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
            Templates are free. Customize after.
          </p>
          <button
            type="button"
            onClick={submit}
            disabled={submitting}
            className="px-5 py-2 rounded-full bg-foreground text-background font-medium hover:bg-foreground/90 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60 transition-colors flex items-center gap-2"
          >
            {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
            {submitting ? "Building…" : "Use this template"}
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
