"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, Globe, Loader2, AlertCircle, CheckCircle2, Sparkles } from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { migrateFromUrl, type MigrateResponse } from "@/lib/api";
import { patchBrief } from "@/lib/state";

/**
 * /migrate — pre-fill the intake from an existing public URL.
 *
 * Pebble's version of Base44's "Migrate from another platform" entry,
 * reworded and reshaped. The user pastes their existing site URL; we
 * pull semantic facts (title, headings, contact info, industry hint)
 * via /api/migrate and show them what we found. They confirm or edit,
 * then proceed into the regular intake flow with the brief pre-populated.
 *
 * NOTHING is copied from the source site — no markup, no styling, no
 * images. We extract FACTS to spare the user from re-typing.
 */
export default function MigratePage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<MigrateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleScan(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const res = await migrateFromUrl(url.trim());
      setResult(res);
      if (!res.ok && res.error) setError(res.error);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  function handleContinue() {
    if (!result) return;
    patchBrief(result.brief_partial);
    router.push("/intake");
  }

  return (
    <div className="min-h-screen flex flex-col">
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
              <Sparkles className="w-3 h-3" /> Coming from another platform?
            </div>
            <h1 className="font-display text-4xl md:text-5xl font-bold text-foreground">
              Bring your site over without retyping it.
            </h1>
            <p className="text-lg text-muted-foreground max-w-xl mx-auto">
              Paste your current URL and I&apos;ll pull the basics — name, contact info,
              what you do. You confirm, I rebuild it the Pebble way.
            </p>
          </motion.div>

          <motion.form
            onSubmit={handleScan}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15, duration: 0.4 }}
            className="bg-card border border-border rounded-2xl p-6 shadow-[var(--shadow-1)]"
          >
            <label htmlFor="migrate-url" className="block text-sm font-semibold text-muted-foreground mb-2">
              Your current site
            </label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  id="migrate-url"
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="yourexistingsite.com"
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
              I only read the public page — nothing copied, no styles taken. Just facts.
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

          <AnimatePresence>
            {result && result.ok && (
              <motion.div
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
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
                    value={result.brief_partial.business_name}
                    placeholder="What should I call your business?"
                    onChange={(v) =>
                      setResult({
                        ...result,
                        brief_partial: { ...result.brief_partial, business_name: v },
                      })
                    }
                  />
                  <ExtractField
                    label="Industry / type"
                    value={result.brief_partial.business_type || ""}
                    placeholder="bakery, plumbing, real_estate…"
                    onChange={(v) =>
                      setResult({
                        ...result,
                        brief_partial: { ...result.brief_partial, business_type: v },
                      })
                    }
                  />
                  <ExtractField
                    label="What I'll use as context"
                    value={result.brief_partial.extra_context}
                    placeholder="Anything we need to know about the business…"
                    multiline
                    onChange={(v) =>
                      setResult({
                        ...result,
                        brief_partial: { ...result.brief_partial, extra_context: v },
                      })
                    }
                  />

                  {result.extract.headings.length > 0 && (
                    <details className="text-sm">
                      <summary className="cursor-pointer text-muted-foreground hover:text-foreground transition-colors">
                        Show everything I found ({result.extract.headings.length} headings,
                        {" " + result.extract.image_count} images
                        {result.extract.color_hints.length ? `, ${result.extract.color_hints.length} colors` : ""})
                      </summary>
                      <div className="mt-3 pl-3 border-l-2 border-border space-y-3">
                        {result.extract.headings.length > 0 && (
                          <div>
                            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">Headings</p>
                            <ul className="text-sm space-y-0.5 text-foreground/80">
                              {result.extract.headings.slice(0, 8).map((h, i) => (
                                <li key={i}>· {h}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {result.extract.phone && (
                          <p className="text-sm">
                            <span className="font-bold">Phone:</span>{" "}
                            <span className="font-mono">{result.extract.phone}</span>
                          </p>
                        )}
                        {result.extract.emails.length > 0 && (
                          <p className="text-sm">
                            <span className="font-bold">Emails:</span>{" "}
                            <span className="font-mono">{result.extract.emails.join(", ")}</span>
                          </p>
                        )}
                        {result.extract.color_hints.length > 0 && (
                          <div>
                            <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground mb-1">Colors</p>
                            <div className="flex gap-1.5">
                              {result.extract.color_hints.slice(0, 8).map((c) => (
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
                      onClick={handleContinue}
                      className="bg-primary text-primary-foreground px-5 py-2.5 rounded-lg font-semibold text-sm hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                    >
                      Use this and continue <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
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
