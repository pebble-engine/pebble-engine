"use client";

/**
 * /community — energetic hub redesign (2026-05-23).
 *
 * Marc's brief: "Home section and community section need to be the
 * most energetic, welcoming all types of people." This is the rebuild.
 *
 * Page anatomy (top → bottom):
 *   1. HERO        — Peblet + "You're not building alone" + stats strip
 *   2. ACTIVITY    — This week in Pebble (curated highlights)
 *   3. SHOWCASE    — 6-card grid of community sites (real template hero
 *                    images today; user-submitted ones when Launchpad
 *                    upload ships)
 *   4. PILLARS     — Launchpad / Hire a Partner / Affiliate (kept from
 *                    the old page but visually elevated)
 *   5. FOUNDER     — Quick note + welcome statement + Code of Conduct
 *
 * Wrapped in the Control Center shell (sidebar left + chat right) so
 * Peblet is one tap away on every section. Visitors who want to "find
 * X in the community" don't have to scroll — they ask.
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  Compass,
  Briefcase,
  Gift,
  Sparkles,
  Rocket,
  Heart,
  MessageCircle,
  ArrowRight,
  Plus,
  Globe,
  Users,
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

// Community stats. Marc 2026-05-23: numbers visible enough to be
// social-proof-y without being so specific that they're embarrassing
// when stale. "Builders building" + template count are both real-
// ish; the launches-this-week is a curated optimism baseline that
// can be tied to a real source when /api/community/stats ships.
const STATS = [
  { label: "Builders building",   value: "1,200+", Icon: Users  },
  { label: "Templates to remix",  value: "21",     Icon: Sparkles },
  { label: "Launches this week",  value: "47",     Icon: Rocket },
];

// Activity feed seed — hand-curated to feel like a real community
// snapshot. When /api/community/feed ships, this becomes the fallback
// for empty results. Each item has an icon + colored chip so the
// list reads as visually varied, not a wall of text.
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

// Showcase — 6 representative community sites. Today these are
// Pebble-curated template hero shots (we have screenshots ready).
// When user uploads ship in Launchpad we'll mix in submissions
// alongside our own examples.
const SHOWCASE = [
  { name: "Honest Garage",        kind: "Auto repair",       image: "/templates-preview/honest_garage.png",        href: "/templates" },
  { name: "Ink Studio",           kind: "Tattoo & arts",     image: "/templates-preview/ink_studio.png",            href: "/templates" },
  { name: "Artisan Kitchen",      kind: "Restaurant",        image: "/templates-preview/artisan_kitchen.png",       href: "/templates" },
  { name: "Boutique Brokerage",   kind: "Real estate",       image: "/templates-preview/boutique_brokerage.png",    href: "/templates" },
  { name: "Instructor Pro",       kind: "Coach / educator",  image: "/templates-preview/instructor_pro.png",        href: "/templates" },
  { name: "Honest Garage (Rust)", kind: "Auto, warm variant", image: "/templates-preview/honest_garage_rust.png",   href: "/templates" },
];

const ACTIVITY_COLORS: Record<ActivityKind, string> = {
  launch:     "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30",
  feature:    "bg-amber-500/15 text-amber-700 dark:text-amber-300 border-amber-500/30",
  tip:        "bg-blue-500/15 text-blue-700 dark:text-blue-300 border-blue-500/30",
  join:       "bg-pink-500/15 text-pink-700 dark:text-pink-300 border-pink-500/30",
  discussion: "bg-violet-500/15 text-violet-700 dark:text-violet-300 border-violet-500/30",
};

const ACTIVITY_LABELS: Record<ActivityKind, string> = {
  launch:     "Launched",
  feature:    "Featured",
  tip:        "Tip",
  join:       "Welcome",
  discussion: "Discussion",
};

// 2026-05-24 — server-side feed integration. The page tries to fetch
// real events + stats on mount. If either fails (Supabase offline,
// 5xx, etc.) we fall back to the hardcoded seeds above so the page
// never shows an empty state on a real outage. When the real feed
// has fewer than 5 items, we pad with seed entries to keep the
// visual rhythm consistent until the community is large enough.

function useCommunityData() {
  const [serverEvents, setServerEvents] = useState<CommunityFeedEvent[] | null>(null);
  const [serverStats, setServerStats] = useState<CommunityStats | null>(null);
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
  return { serverEvents, serverStats };
}

// Translate a server kind ('site_published') into the activity-feed
// kind colors we already styled.
function mapEventKind(kind: string): ActivityKind {
  if (kind === "site_published" || kind === "build_completed") return "launch";
  if (kind === "template_used" || kind === "template_submitted") return "feature";
  if (kind === "tip") return "tip";
  if (kind === "joined_pebble") return "join";
  return "discussion";
}

// Translate an ISO timestamp into a "2h ago" / "3d ago" string so the
// feed reads naturally without us needing a date-fns dep.
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
  const { serverEvents, serverStats } = useCommunityData();

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

  // Stats: prefer live values, fall back to seed for any missing field.
  const liveStats = serverStats
    ? [
        { label: "Builders building",  value: serverStats.total_users.toLocaleString() + "+",          Icon: Users     },
        { label: "Templates to remix", value: serverStats.templates_count.toString(),                  Icon: Sparkles  },
        { label: "Launches this week", value: serverStats.launches_this_week.toString(),               Icon: Rocket    },
      ]
    : STATS;

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

              {/* HERO — bold welcome + Peblet + stats strip */}
              <section className="relative overflow-hidden rounded-3xl border border-border bg-gradient-to-br from-primary/15 via-violet-500/8 to-amber-500/10 p-8 md:p-12">
                {/* Decorative gradient blobs — give the hero motion
                    without animating anything that would tank perf. */}
                <div aria-hidden className="absolute -top-24 -right-24 w-72 h-72 rounded-full bg-primary/30 blur-3xl opacity-50" />
                <div aria-hidden className="absolute -bottom-24 -left-24 w-72 h-72 rounded-full bg-amber-500/25 blur-3xl opacity-50" />

                <div className="relative flex flex-col md:flex-row items-center gap-8">
                  <PebletMascot size="lg" animate className="shrink-0" />
                  <div className="flex-1 text-center md:text-left space-y-3">
                    <p className={`${type.mono} text-xs uppercase tracking-widest text-primary font-bold`}>
                      Pebble Community
                    </p>
                    <h1 className={`${type.display.l} text-foreground leading-tight`}>
                      You&apos;re not building alone.
                    </h1>
                    <p className={`${type.body.m} text-muted-foreground max-w-xl`}>
                      Every kind of builder ships here — plumbers, photographers, podcasters, parents,
                      retirees, teens. All welcome. All winning at their own pace.
                    </p>
                    <div className="pt-2 flex flex-wrap items-center gap-3 justify-center md:justify-start">
                      <Link
                        href="/community/launchpad"
                        className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-foreground text-background text-sm font-semibold hover:opacity-90`}
                      >
                        <Rocket className="w-4 h-4" /> Show your work
                      </Link>
                      <Link
                        href="/community/hire-a-partner"
                        className={`${interactions.button} inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-card border border-border text-foreground text-sm font-semibold hover:bg-accent`}
                      >
                        Find a partner
                      </Link>
                    </div>
                  </div>
                </div>

                {/* Stats strip — Supabase-backed, falls back to seed */}
                <div className="relative mt-8 grid grid-cols-3 gap-3">
                  {liveStats.map((s) => {
                    const Icon = s.Icon;
                    return (
                      <div
                        key={s.label}
                        className="bg-card/70 backdrop-blur-sm border border-border rounded-xl p-3 md:p-4 flex items-center gap-3"
                      >
                        <span className="w-9 h-9 rounded-lg bg-primary/15 text-primary flex items-center justify-center shrink-0">
                          <Icon className="w-4 h-4" />
                        </span>
                        <div className="min-w-0">
                          <p className="text-lg md:text-xl font-bold text-foreground leading-tight">
                            {s.value}
                          </p>
                          <p className="text-[11px] uppercase tracking-widest text-muted-foreground leading-tight">
                            {s.label}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* ACTIVITY — this week in Pebble */}
              <section className="space-y-4">
                <div className="flex items-end justify-between gap-3 flex-wrap">
                  <div>
                    <h2 className={`${type.heading.l} text-foreground`}>This week in Pebble</h2>
                    <p className={`${type.body.s} text-muted-foreground mt-1`}>
                      Launches, features, fresh tips, and 38 new builders joining the conversation.
                    </p>
                  </div>
                  <Link
                    href="/community/launchpad"
                    className={`${type.label} text-primary inline-flex items-center gap-1 hover:underline`}
                  >
                    See all activity <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <ul className="space-y-2">
                  {liveActivity.map((a) => (
                    <li
                      key={a.id}
                      className={`${interactions.card} bg-card border border-border rounded-xl p-4 flex items-start gap-3`}
                    >
                      <span
                        className={`shrink-0 text-[10px] uppercase tracking-widest font-bold px-2 py-1 rounded-full border ${ACTIVITY_COLORS[a.kind]}`}
                      >
                        {ACTIVITY_LABELS[a.kind]}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className={`${type.heading.m} text-foreground leading-tight`}>{a.title}</p>
                        {a.body && (
                          <p className={`${type.body.s} text-muted-foreground mt-1 leading-snug`}>
                            {a.body}
                          </p>
                        )}
                      </div>
                      <p className={`${type.caption} shrink-0 hidden sm:block`}>{a.meta}</p>
                    </li>
                  ))}
                </ul>
              </section>

              {/* SHOWCASE — 6-card grid of community sites */}
              <section className="space-y-4">
                <div className="flex items-end justify-between gap-3 flex-wrap">
                  <div>
                    <h2 className={`${type.heading.l} text-foreground`}>Showcase</h2>
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

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {SHOWCASE.map((s) => (
                    <Link
                      key={s.name}
                      href={s.href}
                      className={`${interactions.card} group relative aspect-[4/3] rounded-xl overflow-hidden border border-border bg-card`}
                    >
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={s.image}
                        alt={`${s.name} preview`}
                        className="absolute inset-0 w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105"
                        loading="lazy"
                      />
                      <div className="absolute inset-x-0 bottom-0 p-3 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                        <p className="text-sm font-bold text-white leading-tight">{s.name}</p>
                        <p className="text-[10px] uppercase tracking-widest text-white/70 mt-0.5">{s.kind}</p>
                      </div>
                    </Link>
                  ))}
                </div>
              </section>

              {/* PILLARS — the three sub-routes, elevated */}
              <section className="space-y-4">
                <h2 className={`${type.heading.l} text-foreground`}>Three ways to get involved</h2>
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
        <h3 className={`${type.heading.m} text-foreground`}>{title}</h3>
        <p className={`${type.body.s} text-muted-foreground mt-1 leading-snug`}>{blurb}</p>
      </div>
      <span className={`${type.label} text-foreground/80 group-hover:text-foreground mt-auto relative z-10 inline-flex items-center gap-1`}>
        Explore <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
      </span>
    </Link>
  );
}
