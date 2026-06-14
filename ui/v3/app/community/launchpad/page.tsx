"use client";

/**
 * /community/launchpad — Batch D v1 (2026-06-12).
 *
 * Public gallery of builder-submitted published sites + owner submit flow.
 */

import React, { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Compass,
  Loader2,
  Rocket,
  Sparkles,
  Trash2,
} from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import {
  fetchLaunchpadShowcase,
  getProjectLaunchpad,
  listProjects,
  submitToLaunchpad,
  withdrawFromLaunchpad,
  type LaunchpadEntry,
  type ProjectLaunchpadState,
} from "@/lib/api";
import { useAuth } from "@/components/auth-provider";

type EligibleProject = ProjectLaunchpadState & { business_name: string };

const FALLBACK_SHOWCASE: Array<{ name: string; kind: string; image: string; href: string }> = [
  { name: "Cinematic Hero",     kind: "Service business", image: "/templates-preview/cinematic_hero.png",    href: "/templates" },
  { name: "Ink Studio",         kind: "Tattoo & arts",    image: "/templates-preview/ink_studio.png",         href: "/templates" },
  { name: "Artisan Kitchen",    kind: "Restaurant",       image: "/templates-preview/artisan_kitchen.png",    href: "/templates" },
  { name: "Boutique Brokerage", kind: "Real estate",      image: "/templates-preview/boutique_brokerage.png", href: "/templates" },
  { name: "Instructor Pro",     kind: "Coach / educator", image: "/templates-preview/instructor_pro.png",     href: "/templates" },
  { name: "Marlowe Bay",        kind: "Wedding planner",  image: "/templates-preview/cinematic_hero.png",     href: "/templates" },
];

function ShowcaseCard({ entry }: { entry: LaunchpadEntry }) {
  const href = entry.url || entry.preview_url;
  const image = entry.screenshot_url || "/templates-preview/cinematic_hero.png";
  const kind = entry.industry || "Pebble site";

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`${interactions.card} group relative aspect-[4/3] rounded-xl overflow-hidden border border-border bg-card block`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={image}
        alt={`${entry.business_name} preview`}
        className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
        <p className="text-sm font-bold text-white leading-tight">{entry.business_name}</p>
        <p className="text-[10px] uppercase tracking-widest text-white/70 mt-0.5">{kind}</p>
        {entry.tagline && (
          <p className="text-[11px] text-white/80 mt-1 line-clamp-2">{entry.tagline}</p>
        )}
      </div>
    </a>
  );
}

function FallbackCard({ item }: { item: (typeof FALLBACK_SHOWCASE)[number] }) {
  return (
    <Link
      href={item.href}
      className={`${interactions.card} group relative aspect-[4/3] rounded-xl overflow-hidden border border-border bg-card`}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={item.image}
        alt={`${item.name} preview`}
        className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
        <p className="text-sm font-bold text-white leading-tight">{item.name}</p>
        <p className="text-[10px] uppercase tracking-widest text-white/70 mt-0.5">{item.kind}</p>
      </div>
    </Link>
  );
}

export default function LaunchpadPage() {
  const { user } = useAuth();
  const [entries, setEntries] = useState<LaunchpadEntry[] | null>(null);
  const [loadError, setLoadError] = useState(false);
  const [eligible, setEligible] = useState<EligibleProject[]>([]);
  const [selectedSlug, setSelectedSlug] = useState("");
  const [tagline, setTagline] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitMsg, setSubmitMsg] = useState<string | null>(null);

  const reloadShowcase = useCallback(async () => {
    try {
      const res = await fetchLaunchpadShowcase();
      setEntries(res.entries || []);
      setLoadError(false);
    } catch {
      setEntries([]);
      setLoadError(true);
    }
  }, []);

  useEffect(() => {
    void reloadShowcase();
  }, [reloadShowcase]);

  useEffect(() => {
    if (!user) return;
    void (async () => {
      try {
        const res = await listProjects();
        const list = res.projects || [];
        const published: EligibleProject[] = [];
        await Promise.all(
          list.map(async (p) => {
            try {
              const st = await getProjectLaunchpad(p.slug);
              if (st.published) {
                published.push({
                  ...st,
                  business_name: p.business_name || p.slug,
                });
              }
            } catch {
              /* skip */
            }
          }),
        );
        setEligible(published);
        if (published.length && !selectedSlug) {
          setSelectedSlug(published[0].slug);
        }
      } catch {
        setEligible([]);
      }
    })();
  }, [user, selectedSlug]);

  const selected = eligible.find((p) => p.slug === selectedSlug);

  const handleSubmit = async () => {
    if (!selectedSlug) return;
    setSubmitting(true);
    setSubmitMsg(null);
    try {
      await submitToLaunchpad(selectedSlug, tagline.trim() ? { tagline: tagline.trim() } : undefined);
      setEligible((prev) =>
        prev.map((p) => (p.slug === selectedSlug ? { ...p, submitted: true } : p)),
      );
      setSubmitMsg("You're on the Launchpad — thanks for sharing!");
      setTagline("");
      await reloadShowcase();
    } catch (e) {
      setSubmitMsg(e instanceof Error ? e.message : "Submit failed — try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleWithdraw = async (slug: string) => {
    setSubmitting(true);
    setSubmitMsg(null);
    try {
      await withdrawFromLaunchpad(slug);
      setEligible((prev) =>
        prev.map((p) => (p.slug === slug ? { ...p, submitted: false, entry: null } : p)),
      );
      setSubmitMsg("Removed from the gallery.");
      await reloadShowcase();
    } catch (e) {
      setSubmitMsg(e instanceof Error ? e.message : "Could not remove — try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const galleryEmpty = !loadError && entries !== null && entries.length === 0;
  const useFallback = loadError || galleryEmpty;

  return (
    <DashboardLayout topNavLabel="Launchpad">
      <div className="p-6 md:p-8">
        <div className="max-w-6xl mx-auto space-y-10">
          <header className="text-center space-y-3 pt-4">
            <div className="inline-flex w-14 h-14 rounded-2xl bg-primary/10 text-primary items-center justify-center">
              <Compass className="w-7 h-7" />
            </div>
            <h1 className={`${type.dashboard.display.l} text-foreground`}>Launchpad</h1>
            <p className={`${type.body.m} text-muted-foreground max-w-2xl mx-auto`}>
              A public gallery where Pebble builders showcase what they shipped.
              Publish your site, submit it here, and inspire the next person to start.
            </p>
          </header>

          {user ? (
            <section className="bg-card border border-border rounded-2xl p-6 space-y-4">
              <h2 className={`${type.dashboard.heading.m} text-foreground`}>Share your site</h2>
              {eligible.length === 0 ? (
                <p className={`${type.body.s} text-muted-foreground`}>
                  Publish a project first — then you can add it to the gallery.
                  <Link href="/dashboard" className="text-primary ml-1 hover:underline">Go to projects</Link>
                </p>
              ) : (
                <>
                  <div className="flex flex-col sm:flex-row gap-3">
                    <select
                      value={selectedSlug}
                      onChange={(e) => setSelectedSlug(e.target.value)}
                      className="flex-1 rounded-xl border border-border bg-background px-3 py-2 text-sm"
                    >
                      {eligible.map((p) => (
                        <option key={p.slug} value={p.slug}>
                          {p.business_name}
                          {p.submitted ? " (in gallery)" : ""}
                        </option>
                      ))}
                    </select>
                    <input
                      type="text"
                      value={tagline}
                      onChange={(e) => setTagline(e.target.value)}
                      placeholder="Optional one-liner (what makes this site special)"
                      className="flex-[2] rounded-xl border border-border bg-background px-3 py-2 text-sm"
                      maxLength={280}
                    />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selected?.submitted ? (
                      <button
                        type="button"
                        disabled={submitting}
                        onClick={() => void handleWithdraw(selectedSlug)}
                        className={`${interactions.chip} inline-flex items-center gap-2 px-4 py-2 rounded-full border border-border text-sm font-semibold`}
                      >
                        <Trash2 className="w-4 h-4" /> Remove from gallery
                      </button>
                    ) : (
                      <button
                        type="button"
                        disabled={submitting || !selectedSlug}
                        onClick={() => void handleSubmit()}
                        className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2 rounded-full bg-primary text-primary-foreground text-sm font-bold`}
                      >
                        {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
                        Submit to Launchpad
                      </button>
                    )}
                  </div>
                </>
              )}
              {submitMsg && (
                <p className={`${type.body.s} text-muted-foreground`}>{submitMsg}</p>
              )}
            </section>
          ) : (
            <section className="bg-card/60 border border-dashed border-border rounded-2xl p-6 text-center">
              <p className={`${type.body.s} text-muted-foreground`}>
                <Link href="/login?redirect=/community/launchpad" className="text-primary font-semibold hover:underline">
                  Sign in
                </Link>
                {" "}to submit a published site to the gallery.
              </p>
            </section>
          )}

          <section className="space-y-4">
            <div className="flex items-end justify-between gap-3 flex-wrap">
              <div>
                <h2 className={`${type.dashboard.heading.l} text-foreground`}>Showcase</h2>
                <p className={`${type.body.s} text-muted-foreground mt-1`}>
                  {galleryEmpty && !loadError
                    ? "Be the first builder in the gallery — submit a published site above."
                    : "Real sites built with Pebble. Click to visit live."}
                </p>
              </div>
              <Link
                href="/"
                className={`${type.label} text-primary inline-flex items-center gap-1 hover:underline`}
              >
                <Sparkles className="w-3.5 h-3.5" /> Build yours
              </Link>
            </div>

            {entries === null && (
              <p className={`${type.body.s} text-muted-foreground`}>Loading gallery…</p>
            )}

            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {!useFallback && entries?.map((e) => (
                <ShowcaseCard key={e.slug} entry={e} />
              ))}
              {useFallback && FALLBACK_SHOWCASE.map((item) => (
                <FallbackCard key={item.name + item.kind} item={item} />
              ))}
            </div>

            {loadError && (
              <p className={`${type.caption} text-muted-foreground`}>
                Live gallery unavailable — showing template previews until the API reconnects.
              </p>
            )}
          </section>

          <section className="text-center pb-8">
            <Link
              href="/community"
              className={`${interactions.chip} inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-border text-sm font-semibold`}
            >
              Back to Community
            </Link>
          </section>
        </div>
      </div>
    </DashboardLayout>
  );
}
