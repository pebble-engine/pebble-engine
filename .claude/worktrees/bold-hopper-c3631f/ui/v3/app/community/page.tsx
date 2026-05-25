"use client";

/**
 * /community — cinematic rebuild (2026-05-25).
 *
 * Page anatomy (top → bottom):
 *   1. HERO        — Full-bleed dark photo + centered massive serif headline
 *                    + "This week in Pebble" subtitle + dot-ticker + pill CTAs
 *   2. SHOWCASE    — Dense filmstrip (160px wide cards, aspect-square)
 *   3. PILLARS     — Launchpad / Hire a Partner / Affiliate
 *   4. FOUNDER     — Peblet welcome note + Code of Conduct
 *
 * Sections removed vs previous version:
 *   - Stats strip (frosted glass tiles inside hero)
 *   - Activity card list ("This week in Pebble" body cards)
 *   - Marquee news ticker
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Compass,
  Briefcase,
  Gift,
  Rocket,
  Heart,
  MessageCircle,
  ArrowRight,
  Plus,
  Globe,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { ControlCenter } from "@/components/control-center";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { PebletMascot } from "@/components/peblet-mascot";
import { NotificationBell } from "@/components/notification-bell";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import {
  fetchCommunityFeed,
  fetchCommunityStats,
  type CommunityFeedEvent,
  type CommunityStats,
} from "@/lib/api";

// Activity feed seed — hand-curated to feel like a real community
// snapshot. When /api/community/feed ships, this becomes the fallback
// for empty results.
type ActivityKind = "launch" | "feature" | "tip" | "join" | "discussion";
const ACTIVITY: Array<{
  id:    string;
  kind:  ActivityKind;
  title: string;
  body:  string;
  meta:  string;
}> = [
  {
    id:    "f-honest-garage",
    kind:  "feature",
    title: "Honest Garage got featured",
    body:  "Mechanic shop in Brooklyn pulled in 90 leads in their first week — a Launchpad spotlight pick.",
    meta:  "2 hours ago",
  },
  {
    id:    "t-domain",
    kind:  "tip",
    title: "Custom domain in one DNS record",
    body:  "A new walkthrough from the Pebble docs — sub-5-minute setup, no waiting on tech support.",
    meta:  "4 hours ago",
  },
  {
    id:    "j-batch",
    kind:  "join",
    title: "Welcome to 38 new builders",
    body:  "Plumbers, photographers, bakeries, a yoga studio, and one wedding planner from Lisbon. Say hi.",
    meta:  "this week",
  },
  {
    id:    "d-mobile",
    kind:  "discussion",
    title: "What's the best mobile-first DNA?",
    body:  "Open thread — share which DNA card works best for thumb-driven traffic.",
    meta:  "yesterday",
  },
  {
    id:    "l-marlowe",
    kind:  "launch",
    title: "Marlowe Bay Weddings is live",
    body:  "Coastal wedding planner — Gallery First layout, garden press DNA. Marlowe submitted to the Launchpad.",
    meta:  "2 days ago",
  },
];

// Showcase — 6 representative community sites.
const SHOWCASE = [
  { name: "Cinematic Hero",       kind: "Service business",  image: "/templates-preview/cinematic_hero.png",       href: "/templates" },
  { name: "Ink Studio",           kind: "Tattoo & arts",     image: "/templates-preview/ink_studio.png",            href: "/templates" },
  { name: "Artisan Kitchen",      kind: "Restaurant",        image: "/templates-preview/artisan_kitchen.png",       href: "/templates" },
  { name: "Boutique Brokerage",   kind: "Real estate",       image: "/templates-preview/boutique_brokerage.png",    href: "/templates" },
  { name: "Instructor Pro",       kind: "Coach / educator",  image: "/templates-preview/instructor_pro.png",        href: "/templates" },
  { name: "Honest Garage",        kind: "Auto repair",       image: "/templates-preview/honest_garage.png",         href: "/templates" },
];

// 2026-05-24 — server-side feed integration. Fallback to seed if server
// returns fewer than 5 items or errors out.
function useCommunityData() {
  const [serverEvents, setServerEvents] = useState<CommunityFeedEvent[] | null>(null);
  // Stats fetch kept for future use but not rendered in this design.
  const [, setServerStats] = useState<CommunityStats | null>(null);
  useEffect(() => {
    void (async () => {
      try {
        const res = await fetchCommunityFeed();
        setServerEvents(res.events || []);
      } catch {
        setServerEvents([]);
      }
      try {
        const res = await fetchCommunityStats();
        setServerStats(res.stats || null);
      } catch {
        setServerStats(null);
      }
    })();
  }, []);
  return { serverEvents };
}

// Translate a server kind ('site_published') into the activity-feed kind.
function mapEventKind(kind: string): ActivityKind {
  if (kind === "site_published" || kind === "build_completed") return "launch";
  if (kind === "template_used" || kind === "template_submitted") return "feature";
  if (kind === "tip") return "tip";
  if (kind === "joined_pebble") return "join";
  return "discussion";
}

// Translate an ISO timestamp into a "2h ago" string.
function relativeTime(iso: string): string {
  try {
    const then = new Date(iso).getTime();
    const diff = (Date.now() - then) / 1000;
    if (diff < 60) return "just now";
    if (diff < 3600) return `${Math.floor(diff / 60)} min ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
    return new Date(iso).toLocaleDateString();
  } catch {
    return "";
  }
}

export default function CommunityHomePage() {
  const { serverEvents } = useCommunityData();

  // Merge: server events first, fill to 5 with seed if we're light.
  const liveActivity = (() => {
    const fromServer = (serverEvents || []).map((e) => ({
      id:    `srv-${e.id}`,
      kind:  mapEventKind(e.kind),
      title: e.title,
      body:  e.body || "",
      meta:  relativeTime(e.created_at),
    }));
    if (fromServer.length >= 5) return fromServer.slice(0, 5);
    const padding = ACTIVITY.slice(0, 5 - fromServer.length);
    return [...fromServer, ...padding];
  })();

  const topRightSlot = (
    <div className="flex items-center gap-2">
      <Link
        href="/workspace#phase=welcome"
        className={`${interactions.button} inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-primary text-primary-foreground text-sm font-semibold hover:opacity-90 transition-opacity`}
      >
        <Plus className="w-4 h-4" />
        New project
      </Link>
      <NotificationBell />
    </div>
  );

  const greeting =
    "Welcome to the community. I can show you launches, partners, or affiliate stuff — what do you want to see?";

  return (
    <div className="flex flex-col h-screen-safe">
      <TopNav projectName="Community" rightSlot={topRightSlot} />
      <div className="flex-1 min-h-0">
        <ControlCenter greeting={greeting} leftSidebar={<DashboardSidebar />}>
          <div className="p-6 md:p-8">
            <div className="max-w-6xl mx-auto space-y-10">

              {/* HERO — full-bleed cinematic photo with centered headline + dot-ticker */}
              <section className="relative overflow-hidden rounded-3xl min-h-[560px] md:min-h-[620px] flex flex-col items-center justify-center px-6">
                {/* Background photo — dark creative workspace */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80"
                  alt=""
                  aria-hidden="true"
                  // @ts-expect-error fetchpriority is valid HTML but not in React typedefs yet
                  fetchpriority="high"
                  className="absolute inset-0 w-full h-full object-cover"
                />
                {/* Dark overlay */}
                <div aria-hidden className="absolute inset-0 bg-black/55" />

                {/* Centered content */}
                <div className="relative z-10 text-center space-y-6 max-w-4xl w-full">
                  {/* Massive serif headline */}
                  <h1
                    className="text-5xl md:text-7xl lg:text-8xl text-white leading-[1.05] tracking-tight"
                    style={{ fontFamily: "Georgia, 'Times New Roman', serif" }}
                  >
                    You&apos;re not<br />building alone.
                  </h1>

                  {/* Section caption for the ticker */}
                  <p className={`${type.mono} text-[11px] uppercase tracking-widest text-white/70`}>
                    This week in Pebble
                  </p>

                  {/* Dot-indicator ticker */}
                  <DotTicker
                    items={liveActivity.slice(0, 5).map((a) => ({ id: a.id, title: a.title }))}
                  />

                  {/* Pill CTAs */}
                  <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
                    <Link
                      href="/community/launchpad"
                      className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white text-black text-sm font-semibold hover:opacity-90`}
                    >
                      <Rocket className="w-4 h-4" /> Show your work
                    </Link>
                    <Link
                      href="/community/hire-a-partner"
                      className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/10 border border-white/30 text-white text-sm font-semibold hover:bg-white/20`}
                    >
                      Find a partner
                    </Link>
                  </div>
                </div>
              </section>

              {/* SHOWCASE — dense filmstrip (~160px wide cards) */}
              <section className="space-y-4">
                <div className="flex items-end justify-between gap-3 flex-wrap">
                  <div>
                    <h2 className={`${type.dashboard.heading.l} text-foreground`}>Showcase</h2>
                    <p className={`${type.body.s} text-muted-foreground mt-1`}>
                      Real sites built with Pebble. Steal the structure, swap in your story.
                    </p>
                  </div>
                  <Link
                    href="/community/launchpad"
                    className={`${type.label} text-primary inline-flex items-center gap-1 hover:underline`}
                  >
                    Submit yours <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="relative">
                  {/* Scroll shadows */}
                  <div aria-hidden className="absolute left-0 top-0 bottom-0 w-8 bg-gradient-to-r from-background to-transparent z-10 pointer-events-none" />
                  <div aria-hidden className="absolute right-0 top-0 bottom-0 w-8 bg-gradient-to-l from-background to-transparent z-10 pointer-events-none" />
                  <div className="flex gap-3 overflow-x-auto [&::-webkit-scrollbar]:hidden pb-2 snap-x snap-mandatory">
                    {SHOWCASE.map((s) => (
                      <Link
                        key={`${s.name}-${s.image}`}
                        href={s.href}
                        className={`${interactions.card} group relative shrink-0 snap-start w-[160px] aspect-square rounded-xl overflow-hidden border border-border bg-card`}
                      >
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={s.image}
                          alt={`${s.name} preview`}
                          className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
                          loading="lazy"
                        />
                        <div className="absolute inset-x-0 bottom-0 p-2 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                          <p className="text-xs font-bold text-white leading-tight">{s.name}</p>
                          <p className="text-[9px] uppercase tracking-widest text-white/70 mt-0.5">{s.kind}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>
              </section>

              {/* PILLARS — the three sub-routes */}
              <section className="space-y-4">
                <h2 className={`${type.dashboard.heading.l} text-foreground`}>Three ways to get involved</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Pillar
                    href="/community/launchpad"
                    Icon={Compass}
                    title="Launchpad"
                    blurb="Public showcase of designs, templates, and case studies. Open to all — no plan required to browse."
                    accent="from-emerald-500/15 to-emerald-500/0"
                  />
                  <Pillar
                    href="/community/hire-a-partner"
                    Icon={Briefcase}
                    title="Hire a Partner"
                    blurb="Need a custom build or design polish? Browse vetted Pebble Partners and reach out directly."
                    accent="from-amber-500/15 to-amber-500/0"
                  />
                  <Pillar
                    href="/community/affiliate"
                    Icon={Gift}
                    title="Affiliate Program"
                    blurb="Refer Pebble to friends and earn account credit on every paid plan they start."
                    accent="from-pink-500/15 to-pink-500/0"
                  />
                </div>
              </section>

              {/* FOUNDER NOTE + welcome statement + code of conduct */}
              <section className="rounded-2xl border border-border bg-card p-6 md:p-8 flex flex-col md:flex-row gap-6 items-start">
                <div className="shrink-0">
                  <PebletMascot size="md" />
                </div>
                <div className="flex-1 space-y-3">
                  <p className={`${type.mono} text-[11px] uppercase tracking-widest text-muted-foreground`}>
                    A note from Pebble
                  </p>
                  <p className={`${type.body.m} text-foreground leading-relaxed`}>
                    &ldquo;Everyone here is figuring out a small business website for the first time. Some
                    of us are launching the thing we&apos;ve been thinking about for ten years. Some of us
                    are helping our parents. Some of us are 17 and have never built anything online.
                    All of you are welcome. None of you are asking dumb questions. Peblet is here for the
                    2am ones.&rdquo;
                  </p>
                  <div className="flex flex-wrap items-center gap-3 pt-2">
                    <span className={`${type.mono} text-xs uppercase tracking-widest font-bold px-3 py-1.5 rounded-full bg-pink-500/15 text-pink-700 dark:text-pink-300 border border-pink-500/30 inline-flex items-center gap-1.5`}>
                      <Heart className="w-3 h-3" /> All builders welcome
                    </span>
                    <Link
                      href="/trust"
                      className={`${type.label} text-muted-foreground hover:text-foreground inline-flex items-center gap-1`}
                    >
                      <Globe className="w-3.5 h-3.5" /> Trust Charter
                    </Link>
                    <button
                      type="button"
                      onClick={() => window.postMessage({ type: "pebble-chat-open" }, "*")}
                      className={`${type.label} text-muted-foreground hover:text-foreground inline-flex items-center gap-1`}
                    >
                      <MessageCircle className="w-3.5 h-3.5" /> Ask Peblet
                    </button>
                  </div>
                </div>
              </section>

            </div>
          </div>
        </ControlCenter>
      </div>
    </div>
  );
}

function Pillar({
  href, Icon, title, blurb, accent,
}: {
  href: string;
  Icon: typeof Compass;
  title: string;
  blurb: string;
  accent: string;
}) {
  return (
    <Link
      href={href}
      className={`${interactions.card} group relative overflow-hidden bg-card border border-border rounded-2xl p-6 flex flex-col gap-3 hover:border-primary/40 transition-colors`}
    >
      <div className={`absolute inset-0 -z-0 bg-gradient-to-br ${accent} opacity-100`} />
      <div className="relative z-10 w-12 h-12 rounded-xl bg-foreground text-background flex items-center justify-center group-hover:scale-105 transition-transform">
        <Icon className="w-6 h-6" />
      </div>
      <div className="relative z-10">
        <h3 className={`${type.dashboard.heading.m} text-foreground`}>{title}</h3>
        <p className={`${type.body.s} text-muted-foreground mt-1 leading-snug`}>{blurb}</p>
      </div>
      <span className={`${type.label} text-foreground/80 group-hover:text-foreground mt-auto relative z-10 inline-flex items-center gap-1`}>
        Explore <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
      </span>
    </Link>
  );
}

// DotTicker — static horizontal strip of activity items separated by
// dashed-line + circular dot markers. The middle item is "active"
// (white/90); flanking items are dimmer (white/40).
function DotTicker({ items }: { items: Array<{ id: string; title: string }> }) {
  return (
    <div className="flex items-center justify-center gap-3 md:gap-4 w-full max-w-4xl mx-auto overflow-hidden">
      {items.map((it, i) => {
        const active = i === Math.floor(items.length / 2);
        return (
          <React.Fragment key={it.id}>
            <span
              className={`text-xs md:text-sm whitespace-nowrap ${
                active ? "text-white/90 font-medium" : "text-white/40"
              }`}
            >
              {it.title}
            </span>
            {i < items.length - 1 && (
              <span aria-hidden="true" className="flex items-center gap-1 shrink-0">
                <span className="block w-6 md:w-10 h-px bg-white/30" />
                <span className="block w-1.5 h-1.5 rounded-full bg-white/60" />
                <span className="block w-6 md:w-10 h-px bg-white/30" />
              </span>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
}
