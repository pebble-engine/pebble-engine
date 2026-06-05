"use client";

/**
 * Example Gallery — /examples
 *
 * 2026-05-31. Fifteen complete industry sites built by the v2 motion engine
 * (one per industry across all 7 vibes), offered as FREE pick-from starting
 * points. Unlike /templates (curated skeleton + LLM content-swap), an example
 * is a finished site: "Use this design" is a pure filesystem clone — no LLM,
 * instant, billable:false — that drops the full motion + click-to-edit site
 * into the user's account. They then edit it like any other project.
 *
 * Card preview is the example's real hero image (static, instant). The live
 * preview happens in the workspace once cloned (the workspace spins up the
 * dev server for the new project). See pebble/server/examples.py.
 */
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, Check, X, Loader2, Layers } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { type } from "@/lib/type";
import { listExamples, cloneExample, type ExampleSummary } from "@/lib/api";
import { STANDARD_S, SHORT_S, EASE_CINEMATIC } from "@/lib/motion";

// Human-friendly vibe labels (manifest stores kebab keys).
const VIBE_LABELS: Record<string, string> = {
  "warm-craft": "Warm & Crafted",
  "clean-trust": "Clean & Trustworthy",
  "bold-energetic": "Bold & Energetic",
  "editorial-minimal": "Editorial & Minimal",
  "appetizing-rich": "Appetizing & Rich",
  "luxurious-spa": "Luxurious & Calm",
  "playful-illustrated": "Playful & Bright",
};

function vibeLabel(v: string): string {
  return VIBE_LABELS[v] ?? v.replace(/-/g, " ");
}

export default function ExamplesPage() {
  const router = useRouter();
  const [examples, setExamples] = useState<ExampleSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [picked, setPicked] = useState<ExampleSummary | null>(null);
  const [activeVibe, setActiveVibe] = useState<string>("all");

  useEffect(() => {
    listExamples()
      .then((res) => setExamples(res.examples))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  // Vibe filter chips (in manifest order, de-duped) + "All".
  const vibes = useMemo(() => {
    const seen: string[] = [];
    (examples ?? []).forEach((e) => {
      if (!seen.includes(e.vibe)) seen.push(e.vibe);
    });
    return seen;
  }, [examples]);

  const visible = useMemo(
    () => (examples ?? []).filter((e) => activeVibe === "all" || e.vibe === activeVibe),
    [examples, activeVibe],
  );

  return (
    <div className="min-h-screen-safe flex flex-col bg-background text-foreground">
      <TopNav />
      <main className="flex-1 px-6 md:px-12 lg:px-16 py-12 max-w-7xl mx-auto w-full">
        <header className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full border border-border bg-card text-xs">
            <Sparkles className="w-3.5 h-3.5" />
            <span className={`${type.mono} uppercase tracking-wider`}>Finished sites, free to start from</span>
          </div>
          <h1 className={`${type.dashboard.display.l} mb-3`}>Start from a finished site</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-2xl mx-auto`}>
            Fifteen real, animated sites across industries — built by the same engine you&apos;ll edit
            with. Pick one, make it yours. Every word, color, and image is editable after.
          </p>
        </header>

        {error && (
          <div className="max-w-md mx-auto p-4 rounded-lg border border-red-300 bg-red-50 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-200">
            Couldn&apos;t load the gallery: {error}
          </div>
        )}

        {!examples && !error && (
          <div className="text-center text-muted-foreground py-16">
            <Loader2 className="w-6 h-6 mx-auto mb-3 animate-spin" />
            <p className={type.body.s}>Loading the gallery…</p>
          </div>
        )}

        {/* Vibe filter chips */}
        {examples && examples.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-1.5 mb-8">
            <VibeChip active={activeVibe === "all"} onClick={() => setActiveVibe("all")}>
              All
            </VibeChip>
            {vibes.map((v) => (
              <VibeChip key={v} active={activeVibe === v} onClick={() => setActiveVibe(v)}>
                {vibeLabel(v)}
              </VibeChip>
            ))}
          </div>
        )}

        {examples && visible.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {visible.map((e, i) => (
              <ExampleCard key={e.slug} example={e} index={i} onClick={() => setPicked(e)} />
            ))}
          </div>
        )}

        {examples && examples.length === 0 && !error && (
          <div className="text-center text-muted-foreground py-16">
            <p className={type.body.m}>No examples available yet.</p>
          </div>
        )}
      </main>

      {picked && <CloneDialog example={picked} onClose={() => setPicked(null)} router={router} />}
    </div>
  );
}

// ------------------------------------------------------------------ //
// Example card — real hero image + name + vibe + industry             //
// ------------------------------------------------------------------ //

function ExampleCard({
  example: e,
  index: i,
  onClick,
}: {
  example: ExampleSummary;
  index: number;
  onClick: () => void;
}) {
  const [imgErrored, setImgErrored] = useState(false);
  return (
    <motion.button
      onClick={onClick}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: STANDARD_S, delay: i * 0.04, ease: EASE_CINEMATIC }}
      className="group text-left bg-card border border-border rounded-2xl overflow-hidden hover:border-foreground/30 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
    >
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
        {!imgErrored && e.hero_image ? (
          /* eslint-disable-next-line @next/next/no-img-element */
          <img
            src={e.hero_image}
            alt={`${e.name} preview`}
            className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            loading="lazy"
            onError={() => setImgErrored(true)}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <p className={`${type.dashboard.display.m} opacity-80 px-4 text-center`}>{e.name}</p>
          </div>
        )}
        {/* Free badge — these are always free to clone */}
        <div className="absolute top-3 left-3 px-2.5 py-0.5 rounded-full text-xs uppercase tracking-wider z-10 bg-foreground/85 text-background">
          Free
        </div>
      </div>
      <div className="p-5">
        <div className="flex items-center justify-between gap-2 mb-2">
          <h3 className={`${type.dashboard.heading.m}`}>{e.name}</h3>
          <span
            className="inline-flex items-center gap-1 text-xs text-muted-foreground shrink-0"
            title={`${e.sections} sections`}
            aria-label={`${e.sections} sections`}
          >
            <Layers className="w-3 h-3" aria-hidden />
            {e.sections}
          </span>
        </div>
        <p className={`${type.body.s} text-muted-foreground line-clamp-1 mb-3 capitalize`}>
          {e.industry}
        </p>
        <span
          className={`${type.mono} px-2 py-0.5 rounded-full bg-muted text-xs text-muted-foreground`}
        >
          {vibeLabel(e.vibe)}
        </span>
      </div>
    </motion.button>
  );
}

// ------------------------------------------------------------------ //
// Clone dialog — optional rename + auth-gated clone → workspace       //
// ------------------------------------------------------------------ //

function CloneDialog({
  example,
  onClose,
  router,
}: {
  example: ExampleSummary;
  onClose: () => void;
  router: ReturnType<typeof useRouter>;
}) {
  const [businessName, setBusinessName] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [needsAuth, setNeedsAuth] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Esc closes the modal — standard modal UX (backdrop-click already works).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      // Auth gate — clones land in the user's account, so require a session.
      const { createClient } = await import("@/lib/supabase/client");
      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        setNeedsAuth(true);
        setSubmitting(false);
        return;
      }
      const res = await cloneExample(example.slug, businessName.trim() || undefined);
      if (!res.ok || !res.slug) {
        throw new Error("Clone failed — please try again.");
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
        className="w-full max-w-lg bg-card border border-border rounded-2xl overflow-hidden shadow-2xl"
        onClick={(ev) => ev.stopPropagation()}
      >
        {/* Hero strip */}
        <div className="relative aspect-[16/9] w-full bg-muted">
          {example.hero_image && (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={example.hero_image}
              alt={`${example.name} preview`}
              className="absolute inset-0 w-full h-full object-cover"
            />
          )}
          <button
            type="button"
            onClick={onClose}
            className="absolute top-3 right-3 p-1.5 rounded-md bg-black/40 text-white/90 hover:bg-black/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/60"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <p className={`${type.mono} text-xs uppercase tracking-wider text-muted-foreground mb-1`}>
            {vibeLabel(example.vibe)} · <span className="capitalize">{example.industry}</span>
          </p>
          <h2 className={`${type.dashboard.heading.l} mb-4`}>Start from {example.name}</h2>

          <label className="block">
            <span className={`${type.label} block mb-1.5`}>
              Your business name <span className="text-muted-foreground font-normal">(optional)</span>
            </span>
            <input
              type="text"
              value={businessName}
              onChange={(ev) => setBusinessName(ev.target.value)}
              placeholder={`Leave blank to keep "${example.name}"`}
              className="w-full px-3 py-2 rounded-md bg-background border border-border focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60"
              autoFocus
            />
          </label>

          {needsAuth && (
            <div className="mt-4 flex items-center justify-between gap-3 p-3 rounded-md bg-amber-50 dark:bg-amber-950/60 border border-amber-300 dark:border-amber-800/60">
              <p className="text-amber-900 dark:text-amber-200 text-sm">
                Sign in first — your copy is saved to your account.
              </p>
              <a
                href="/login?next=/examples"
                className="px-3 py-1.5 rounded-full bg-foreground text-background text-sm font-medium hover:bg-foreground/90 shrink-0"
              >
                Sign in →
              </a>
            </div>
          )}

          {error && (
            <div className="mt-4 p-3 rounded-md bg-red-50 dark:bg-red-950 border border-red-300 dark:border-red-900 text-red-900 dark:text-red-200 text-sm">
              {error}
            </div>
          )}

          <div className="mt-6 flex items-center justify-between">
            <p className={`${type.mono} text-xs text-muted-foreground`}>
              <Check className="inline w-3.5 h-3.5 mr-1 text-foreground" />
              Free · copies instantly · edit anything after
            </p>
            <button
              type="button"
              onClick={submit}
              disabled={submitting}
              className="px-5 py-2 rounded-full bg-foreground text-background font-medium hover:bg-foreground/90 disabled:opacity-60 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-foreground/60 transition-colors flex items-center gap-2"
            >
              {submitting && <Loader2 className="w-4 h-4 animate-spin" />}
              {submitting ? "Copying…" : "Use this design"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// ------------------------------------------------------------------ //
// Vibe filter chip                                                    //
// ------------------------------------------------------------------ //

function VibeChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3.5 py-1.5 rounded-full text-sm font-medium transition-colors ${
        active
          ? "bg-foreground text-background"
          : "bg-card border border-border text-muted-foreground hover:text-foreground"
      }`}
    >
      {children}
    </button>
  );
}
