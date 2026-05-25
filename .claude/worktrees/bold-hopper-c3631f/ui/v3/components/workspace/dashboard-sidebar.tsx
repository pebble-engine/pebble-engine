"use client";

/**
 * DashboardSidebar — Phase 45 (2026-05-22).
 *
 * Shared left-nav chrome for every "logged-in workspace" surface:
 * /dashboard, /integrations, /community/*. Modelled on Base44's
 * returning-user workspace pattern (the screenshots Marc shared on
 * 2026-05-22): brand-mark workspace label up top, then a column of
 * verb-icon nav rows, then a Favorites + Recents drawer at the bottom,
 * then the Upgrade-your-plan footer.
 *
 * Why a shared component (not inlining in every page):
 *   - the sidebar isn't trivially state-light — Favorites + Recents
 *     pull live project data, the Upgrade footer reads the subscription
 *     sentinel, and the Community sub-nav expands based on pathname.
 *   - Marc has 3 more pages to add behind it (Integrations, Community,
 *     and the Plan-mode entry point in Phase 46) — re-implementing this
 *     in each page would explode in 4 different ways.
 *
 * Why the data fetching lives HERE and not in a context:
 *   - the sidebar lists projects; /dashboard also lists projects.
 *   - two calls to the same endpoint = no harm (HTTP cache, no DB join
 *     beyond the directory scan). One-shot context wiring would save
 *     <50ms of network and adds a Provider layer that other pages have
 *     to opt into. Not worth it for the first ship; revisit if perf
 *     ever bites.
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Star,
  Clock,
  Search as SearchIcon,
  Sparkles,
  Plug,
  Compass,
  Plus,
  Coins,
  MessageSquare,
} from "lucide-react";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import {
  listProjects,
  fetchUsage,
  fetchSubscription,
  type ProjectSummary,
  type UsageSummary,
  type SubscriptionState,
} from "@/lib/api";
import { getUserProfile } from "@/lib/state";

type IconType = typeof Home;

// Accepts an optional `plan` prop for forward-compat with workspace-shell.
// Currently unused here but preserved so existing callers don't break.
export function DashboardSidebar(_props: { plan?: unknown } = {}) {
  const pathname = usePathname() || "";
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionState | null>(null);
  const [firstName, setFirstName] = useState<string | null>(null);

  useEffect(() => {
    setFirstName(getUserProfile().firstName || null);
    void (async () => {
      try {
        const [p, u, s] = await Promise.all([
          listProjects().catch(() => ({ projects: [] })),
          fetchUsage().catch(() => null),
          fetchSubscription().catch(() => null),
        ]);
        setProjects(p.projects || []);
        setUsage(u);
        setSubscription(s);
      } catch {
        // Sidebar should never block the page on a network error.
      }
    })();
  }, []);

  const favorites = projects.filter((p) => p.starred).slice(0, 4);
  const recents = [...projects]
    .sort((a, b) => (b.built_at || "").localeCompare(a.built_at || ""))
    .slice(0, 4);

  return (
    <aside className="w-[240px] bg-card/70 backdrop-blur-xl border-r border-border/50 p-5 flex flex-col gap-1 min-h-[calc(100vh-4rem)]">
      {/* Workspace label — Base44 calls this the workspace switcher. We
          don't have multi-workspace support yet, so it's read-only. */}
      <div className="mb-5 px-1">
        <p className={`${type.mono} text-muted-foreground`}>
          {firstName ? `${firstName}'s` : "Your"} workspace
        </p>
      </div>

      {/* Primary nav */}
      <NavLink href="/dashboard" Icon={Home} label="Home" active={pathname === "/dashboard"} />
      <NavLink
        href="/dashboard?view=all"
        Icon={Sparkles}
        label="All designs"
        active={false /* same destination as Home for now */}
      />
      <NavLink href="/templates" Icon={Compass} label="Templates" active={pathname.startsWith("/templates")} />
      <NavLink href="/integrations" Icon={Plug} label="Integrations" active={pathname.startsWith("/integrations")} />

      {/* Ask Pebble — opens the FloatingPeblet chat widget. Replaces the old
          Community nav entry; community is still reachable via direct URLs
          and the in-page hero CTAs. Fires window.postMessage so we don't have
          to prop-drill setOpen through the sidebar / shell. FloatingPeblet
          listens for type === "pebble-chat-open". */}
      <button
        type="button"
        onClick={() => {
          window.postMessage({ type: "pebble-chat-open" }, "*");
        }}
        className={`${interactions.chip} w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold bg-primary/10 text-primary hover:bg-primary/20`}
      >
        <MessageSquare className="w-4 h-4 shrink-0" />
        Ask Pebble
      </button>

      {/* Favorites drawer — top starred. Empty state matches Base44. */}
      <SectionHeader>Favorites</SectionHeader>
      {favorites.length === 0 ? (
        <p className={`${type.caption} px-3 py-2 leading-snug`}>
          No favorites yet —<br />star a design to pin it here.
        </p>
      ) : (
        favorites.map((p) => (
          <ProjectLink key={p.slug} slug={p.slug} name={p.business_name} />
        ))
      )}

      {/* Recents drawer — newest first. "View all" goes back to dashboard. */}
      <SectionHeader>Recents</SectionHeader>
      {recents.length === 0 ? (
        <p className={`${type.caption} px-3 py-2 leading-snug`}>
          Nothing yet — build your first design from <Link href="/" className="underline">Home</Link>.
        </p>
      ) : (
        <>
          {recents.map((p) => (
            <ProjectLink key={p.slug} slug={p.slug} name={p.business_name} />
          ))}
          <Link
            href="/dashboard"
            className={`${type.caption} px-3 py-1.5 hover:text-foreground transition-colors`}
          >
            View all →
          </Link>
        </>
      )}

      {/* Footer — Upgrade or Usage. Active subscription = no upgrade prompt. */}
      <div className="mt-auto pt-4 border-t border-border space-y-3">
        {subscription !== null && !subscription?.plan && (() => {
          // FREE_LIMIT mirrors pebble/user_plan.py PLAN_LIMITS["free"]["published_sites"].
          // Counting created projects (not published) per Marc 2026-05-25 —
          // the counter ticks up the moment a project exists, matching what
          // a non-technical user expects from "you have N projects."
          const created = projects.length;
          const FREE_LIMIT = 1;
          const displayCount = Math.min(created, FREE_LIMIT);
          const atLimit = created >= FREE_LIMIT;
          return (
            <div className={`px-3 py-2 bg-background border rounded-lg ${atLimit ? "border-destructive/40" : "border-border"}`}>
              <div className="flex items-center justify-between gap-2">
                <p className={type.eyebrow}>Free plan</p>
                <span className={`text-xs font-bold ${atLimit ? "text-destructive" : "text-muted-foreground"}`}>
                  {displayCount} / {FREE_LIMIT}
                </span>
              </div>
              {atLimit && (
                <Link href="/pricing" className="text-xs text-primary hover:underline mt-1 block">
                  Upgrade for more →
                </Link>
              )}
            </div>
          );
        })()}
        {usage && usage.projects > 0 && (
          <div className="px-3 py-2 bg-background border border-border rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Coins className="w-3.5 h-3.5 text-muted-foreground" />
              <p className={type.eyebrow}>Estimated cost</p>
            </div>
            <p className={`${type.body.s} text-foreground`}>
              ${usage.total_estimated_cost_usd.toFixed(4)}
            </p>
            <p className={`${type.caption} mt-1`}>
              {usage.projects} {usage.projects === 1 ? "build" : "builds"} ·{" "}
              {(usage.total_input_tokens + usage.total_output_tokens).toLocaleString()} tokens
            </p>
          </div>
        )}

        <Link
          href="/"
          className={`${interactions.button} flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-semibold`}
        >
          <Plus className="w-4 h-4" />
          Start something new
        </Link>
      </div>
    </aside>
  );
}

// ---------------------------------------------------------------------------

function NavLink({
  href, Icon, label, active, rightSlot,
}: {
  href: string;
  Icon: IconType;
  label: string;
  active: boolean;
  rightSlot?: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={`${interactions.chip} flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm font-semibold ${
        active
          ? "bg-primary/15 text-primary"
          : "text-muted-foreground hover:text-foreground"
      }`}
    >
      <span className="flex items-center gap-2">
        <Icon className="w-4 h-4" />
        {label}
      </span>
      {rightSlot}
    </Link>
  );
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <div className="mt-4 mb-1 px-3">
      <p className={type.eyebrow}>{children}</p>
    </div>
  );
}

function ProjectLink({ slug, name }: { slug: string; name: string }) {
  return (
    <Link
      href={`/workspace?slug=${encodeURIComponent(slug)}`}
      className={`${interactions.chip} flex items-center gap-2 px-3 py-1.5 rounded-md text-xs text-muted-foreground hover:text-foreground truncate`}
      title={name}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-primary/60 shrink-0" />
      <span className="truncate">{name}</span>
    </Link>
  );
}
