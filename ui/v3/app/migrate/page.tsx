"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Globe, Loader2, AlertCircle, CheckCircle2, Sparkles, Palette, FileText } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import {
  inspireFromUrl,
  migrateFromUrl,
  type InspireResponse,
  type MigrateResponse,
} from "@/lib/api";
import { patchBrief } from "@/lib/state";

/**
 * /migrate — pre-fill the intake from an existing public URL.
 *
 * Two modes, sibling endpoints:
 *
 * 1. **Migrate the content** (`/api/migrate`). The user is *moving over*
 *    from another platform. We extract business FACTS — name, type,
 *    phone, headings — so they don't re-type them. NOTHING about style
 *    is carried over; design is generated fresh against a Pebble DNA.
 *
 * 2. **Use as inspiration** (`/api/inspire`). The user *likes the look*
 *    of some other site. We extract aesthetic SIGNALS — palette,
 *    typography, vibe — and match against a Pebble Style DNA card. The
 *    questionnaire's DNA preview chip auto-selects to that card. No
 *    business facts are carried over.
 *
 * Both modes use the same hardened fetch (`pebble/url_fetch.py`); both
 * post-process the user-pasted URL on the engine side. The UI is just
 * a tab toggle over the same input.
 */

type Mode = "migrate" | "inspire";

type Result =
  | { mode: "migrate"; data: MigrateResponse }
  | { mode: "inspire"; data: InspireResponse };

export default function MigratePage() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("migrate");
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Toggling tabs resets the prior result so the user doesn't see stale
  // content from the other mode. URL field stays — they're likely scanning
  // the same site both ways to compare.
  const switchMode = (next: Mode) => {
    if (next === mode) return;
    setMode(next);
    setResult(null);
    setError(null);
  };

  async function handleScan(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      if (mode === "migrate") {
        const data = await migrateFromUrl(url.trim());
        setResult({ mode: "migrate", data });
        if (!data.ok && data.error) setError(data.error);
      } else {
        const data = await inspireFromUrl(url.trim());
        setResult({ mode: "inspire", data });
        if (!data.ok && data.error) setError(data.error);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  function continueWithMigrate(data: MigrateResponse) {
    patchBrief(data.brief_partial);
    router.push("/workspace#phase=idea");
  }

  function continueWithInspire(data: InspireResponse) {
    // The idea phase's DnaPreview reads _inspire_dna_hint on mount and
    // hydrates to that DNA card. Setting it here is what makes the
    // questionnaire open already attuned to the user's pasted inspiration.
    patchBrief(data.brief_partial);
    router.push("/workspace#phase=idea");
  }

  return (
    <div className="min-h-screen-safe flex flex-col">
      <TopNav />

      <main className="flex-1 px-4 py-16">
        <div className="max-w-3xl mx-auto space-y-10">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="space-y-3 text-center"
          >
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary/15 text-secondary text-xs font-semibold uppercase tracking-widest">
              <Sparkles className="w-3 h-3" /> Already have a URL in mind?
            </div>
            <h1 className="font-display-sans text-4xl md:text-5xl font-bold text-foreground">
              {mode === "migrate"
                ? "Bring your site over without retyping it."
                : "Borrow a look you love."}
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              {mode === "migrate"
                ? "Paste your current URL and I'll pull the basics — name, contact info, what you do. You confirm, I rebuild it the Pebble way."
                : "Paste any URL whose style speaks to you. I'll pull palette, typography, and mood — then match a Pebble DNA card so your build starts in that direction."}
            </p>
          </motion.div>

          <ModeTabs mode={mode} onChange={switchMode} />

          <motion.form
            onSubmit={handleScan}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.4 }}
            className="bg-card border border-border rounded-2xl p-6 shadow-[var(--shadow-1)]"
          >
            <label htmlFor="migrate-url" className="block text-sm font-semibold text-muted-foreground mb-2">
              {mode === "migrate" ? "Your current site" : "A site you'd like the look of"}
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  id="migrate-url"
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder={mode === "migrate" ? "yourexistingsite.com" : "someone-elses-pretty-site.com"}
                  className="w-full pl-9 pr-4 py-3 bg-background border border-border rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-ring"
                  required
                  disabled={busy}
                />
              </div>
              <button
                type="submit"
                disabled={busy || !url.trim()}
                className="bg-primary text-primary-foreground px-6 py-3 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2"
              >
                {busy ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Scanning…
                  </>
                ) : (
                  <>
                    Scan <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 italic">
              {mode === "migrate"
                ? "I only read the public page — nothing copied, no styles taken. Just facts."
                : "I only read the public page — nothing copied. I'm matching the vibe, then generating fresh."}
            </p>
          </motion.form>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex items-start gap-3 p-4 bg-destructive/10 border border-destructive/40 rounded-lg text-destructive text-sm"
              >
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Couldn&apos;t reach that URL.</p>
                  <p className="text-xs opacity-80 mt-1">{error}</p>
                  <p className="text-xs opacity-80 mt-2">
                    No worries — you can still build from scratch.{" "}
                    <Link href="/" className="underline font-semibold">Start fresh →</Link>
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">
            {result && result.mode === "migrate" && result.data.ok && (
              <MigrateResult
                key="migrate-result"
                data={result.data}
                onChange={(next) => setResult({ mode: "migrate", data: next })}
                onContinue={() => continueWithMigrate(result.data)}
              />
            )}
            {result && result.mode === "inspire" && result.data.ok && (
              <InspireResult
                key="inspire-result"
                data={result.data}
                onContinue={() => continueWithInspire(result.data)}
              />
            )}
          </AnimatePresence>

          <div className="text-center">
            <Link
              href="/"
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              ← Back to home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}

/**
 * Two-tab switcher above the URL form. Same visual language as the
 * dashboard's section tabs so it reads as part of Pebble, not a one-off
 * widget. Radio semantics via aria-selected — keyboard users can arrow
 * between tabs.
 */
function ModeTabs({ mode, onChange }: { mode: Mode; onChange: (m: Mode) => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.08, duration: 0.4 }}
      role="tablist"
      aria-label="What to do with the pasted URL"
      className="flex gap-2 p-1 bg-card border border-border rounded-xl max-w-md mx-auto"
    >
      <TabButton
        active={mode === "migrate"}
        onClick={() => onChange("migrate")}
        Icon={FileText}
        label="Migrate the content"
        hint="Carry over the facts"
      />
      <TabButton
        active={mode === "inspire"}
        onClick={() => onChange("inspire")}
        Icon={Palette}
        label="Use as inspiration"
        hint="Borrow the look"
      />
    </motion.div>
  );
}

function TabButton({
  active,
  onClick,
  Icon,
  label,
  hint,
}: {
  active: boolean;
  onClick: () => void;
  Icon: typeof FileText;
  label: string;
  hint: string;
}) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={onClick}
      className={`flex-1 flex flex-col items-start px-4 py-2.5 rounded-lg transition-colors text-left ${
        active
          ? "bg-secondary/15 text-foreground"
          : "text-muted-foreground hover:bg-accent"
      }`}
    >
      <span className="flex items-center gap-1.5 text-sm font-semibold">
        <Icon className={`w-3.5 h-3.5 ${active ? "text-secondary" : ""}`} aria-hidden />
        {label}
      </span>
      <span className="text-[11px] opacity-80">{hint}</span>
    </button>
  );
}

function MigrateResult({
  data,
  onChange,
  onContinue,
}: {
  data: MigrateResponse;
  onChange: (next: MigrateResponse) => void;
  onContinue: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-2 text-secondary">
        <CheckCircle2 className="w-5 h-5" />
        <p className="font-semibold text-sm">Found enough to get started.</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-6 space-y-5">
        <ExtractField
          label="Business name"
          value={data.brief_partial.business_name}
          placeholder="What should I call your business?"
          onChange={(v) =>
            onChange({
              ...data,
              brief_partial: { ...data.brief_partial, business_name: v },
            })
          }
        />
        <ExtractField
          label="Industry / type"
          value={data.brief_partial.business_type || ""}
          placeholder="bakery, plumbing, real_estate…"
          onChange={(v) =>
            onChange({
              ...data,
              brief_partial: { ...data.brief_partial, business_type: v },
            })
          }
        />
        <ExtractField
          label="What I'll use as context"
          value={data.brief_partial.extra_context}
          placeholder="Anything we need to know about the business…"
          multiline
          onChange={(v) =>
            onChange({
              ...data,
              brief_partial: { ...data.brief_partial, extra_context: v },
            })
          }
        />

        {data.extract.headings.length > 0 && (
          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground hover:text-foreground transition-colors">
              Show everything I found ({data.extract.headings.length} headings,
              {" " + data.extract.image_count} images
              {data.extract.color_hints.length ? `, ${data.extract.color_hints.length} colors` : ""})
            </summary>
            <div className="mt-3 pl-3 border-l-2 border-border space-y-3">
              {data.extract.headings.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">Headings</p>
                  <ul className="text-sm space-y-0.5 text-foreground/80">
                    {data.extract.headings.slice(0, 8).map((h, i) => (
                      <li key={i}>· {h}</li>
                    ))}
                  </ul>
                </div>
              )}
              {data.extract.phone && (
                <p className="text-sm">
                  <span className="font-bold">Phone:</span>{" "}
                  <span className="font-mono">{data.extract.phone}</span>
                </p>
              )}
              {data.extract.emails.length > 0 && (
                <p className="text-sm">
                  <span className="font-bold">Emails:</span>{" "}
                  <span className="font-mono">{data.extract.emails.join(", ")}</span>
                </p>
              )}
              {data.extract.color_hints.length > 0 && (
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">Colors</p>
                  <div className="flex gap-1.5">
                    {data.extract.color_hints.slice(0, 8).map((c) => (
                      <div
                        key={c}
                        className="w-6 h-6 rounded-full border border-border"
                        style={{ backgroundColor: c }}
                        title={c}
                      />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </details>
        )}

        <div className="pt-4 border-t border-border flex flex-col sm:flex-row gap-3 justify-end">
          <Link
            href="/"
            className="bg-card border border-border text-foreground px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-accent transition-colors text-center"
          >
            Skip — start fresh
          </Link>
          <button
            onClick={onContinue}
            className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            Use this and continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function InspireResult({ data, onContinue }: { data: InspireResponse; onContinue: () => void }) {
  const { extract } = data;
  const palette = extract.palette;
  // The /api/inspire response includes ALL extracted hex codes — show up
  // to 5, with the classified background+primary+accent labelled below.
  const swatches = (palette.all || []).slice(0, 5);

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      <div className="flex items-center gap-2 text-secondary">
        <CheckCircle2 className="w-5 h-5" />
        <p className="font-semibold text-sm">Got the vibe.</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-6 space-y-6">
        {extract.suggested_dna?.label && (
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">
              Style direction I&apos;ll suggest
            </p>
            <div className="flex items-center gap-3 p-3 rounded-xl bg-secondary/10 border border-secondary/30">
              <Sparkles className="w-5 h-5 text-secondary flex-shrink-0" aria-hidden />
              <div>
                <p className="font-display-sans text-base font-semibold text-foreground">
                  {extract.suggested_dna.label}
                </p>
                <p className="text-xs text-muted-foreground italic">
                  Matched on: {extract.suggested_dna.reason || "default"}
                </p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              The questionnaire&apos;s style strip will open on this one. You can &quot;Try another&quot; from there.
            </p>
          </div>
        )}

        {swatches.length > 0 && (
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Palette</p>
            <div className="flex flex-wrap gap-2">
              {swatches.map((hex) => (
                <div key={hex} className="flex flex-col items-center gap-1">
                  <div
                    className="w-10 h-10 rounded-full border border-border"
                    style={{ backgroundColor: hex }}
                    title={hex}
                  />
                  <span className="font-mono text-[10px] text-muted-foreground">{hex}</span>
                </div>
              ))}
            </div>
            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-[11px] text-muted-foreground">
              {palette.background && <span><b>BG:</b> <span className="font-mono">{palette.background}</span></span>}
              {palette.primary && <span><b>Ink:</b> <span className="font-mono">{palette.primary}</span></span>}
              {palette.accent && <span><b>Accent:</b> <span className="font-mono">{palette.accent}</span></span>}
            </div>
          </div>
        )}

        {(extract.typography?.display || extract.typography?.body) && (
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Typography</p>
            <div className="space-y-1 text-sm">
              {extract.typography.display && (
                <p>
                  <span className="text-muted-foreground">Display:</span>{" "}
                  <span className="font-semibold">{extract.typography.display}</span>
                </p>
              )}
              {extract.typography.body && (
                <p>
                  <span className="text-muted-foreground">Body:</span>{" "}
                  <span className="font-semibold">{extract.typography.body}</span>
                </p>
              )}
            </div>
          </div>
        )}

        {extract.vibe?.descriptors?.length > 0 && (
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-2">Vibe</p>
            <div className="flex flex-wrap gap-1.5">
              {extract.vibe.descriptors.map((d) => (
                <span
                  key={d}
                  className="px-2 py-0.5 rounded-md bg-accent text-[11px] font-semibold capitalize"
                >
                  {d}
                </span>
              ))}
            </div>
          </div>
        )}

        {extract.headline && (
          <div className="text-sm border-l-2 border-border pl-3 italic text-muted-foreground">
            &ldquo;{extract.headline}&rdquo;
          </div>
        )}

        <div className="pt-4 border-t border-border flex flex-col sm:flex-row gap-3 justify-end">
          <Link
            href="/"
            className="bg-card border border-border text-foreground px-5 py-2.5 rounded-lg font-semibold text-sm hover:bg-accent transition-colors text-center"
          >
            Skip — start fresh
          </Link>
          <button
            onClick={onContinue}
            className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
          >
            Use this style and continue <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </motion.div>
  );
}

function ExtractField({
  label,
  value,
  placeholder,
  onChange,
  multiline,
}: {
  label: string;
  value: string;
  placeholder: string;
  onChange: (v: string) => void;
  multiline?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1.5">
        {label}
      </label>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={4}
          className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      )}
    </div>
  );
}
