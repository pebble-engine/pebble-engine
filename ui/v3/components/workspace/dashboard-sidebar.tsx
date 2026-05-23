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
  Users,
  Compass,
  Briefcase,
  Gift,
  Plus,
  Coins,
  ChevronRight,
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

export function DashboardSidebar() {
  const pathname = usePathname() || "";
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [usage, setUsage] = useState<UsageSummary | null>(null);
  const [subscription, setSubscription] = useState<SubscriptionState | null>(null);
  const [firstName, setFirstName] = useState<string | null>(null);

  // Community sub-nav expands when the current path is anywhere under
  // /community. Sticky-open even on Launchpad/Hire/Affiliate so the
  // user always sees their location in the tree.
  const communityOpen = pathname.startsWith("/community");

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
    <aside className="w-[240px] bg-card border-r border-border p-5 flex flex-col gap-1 min-h-[calc(100vh-4rem)]">
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

      {/* Community — expandable. The chevron rotates 90° when open. */}
      <NavLink
        href="/community"
        Icon={Users}
        label="Community"
        active={pathname === "/community"}
        rightSlot={
          <ChevronRight
            className={`w-3.5 h-3.5 text-muted-foreground transition-transform ${communityOpen ? "rotate-90" : ""}`}
          />
        }
      />
      {communityOpen && (
        <div className="ml-3 mt-1 mb-1 flex flex-col gap-1 border-l border-border pl-3">
          <SubNavLink
            href="/community/launchpad"
            Icon={Compass}
            label="Launchpad"
            active={pathname.startsWith("/community/launchpad")}
          />
          <SubNavLink
            href="/community/hire-a-partner"
            Icon={Briefcase}
            label="Hire a Partner"
            active={pathname.startsWith("/community/hire-a-partner")}
          />
          <SubNavLink
            href="/community/affiliate"
            Icon={Gift}
            label="Affiliate Program"
            active={pathname.startsWith("/community/affiliate")}
          />
        </div>
      )}

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
          Nothing yet — <Link href="/workspace#phase=welcome" className="underline">start your first design</Link>.
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
          const published = projects.filter((p) => p.publish != null).length;
          const FREE_LIMIT = 2;
          const atLimit = published >= FREE_LIMIT;
          return (
            <div className={`px-3 py-2 bg-background border rounded-lg ${atLimit ? "border-destructive/40" : "border-border"}`}>
              <div className="flex items-center justify-between gap-2">
                <p className={type.eyebrow}>Free plan</p>
                <span className={`text-xs font-bold ${atLimit ? "text-destructive" : "text-muted-foreground"}`}>
                  {published} / {FREE_LIMIT} live
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
          // Phase 58b — point to /workspace#phase=welcome (the actual idea-
          // capture surface) instead of /. The middleware now redirects
          // signed-in users from / to /dashboard, so linking to / from the
          // dashboard would just loop back here. /workspace#phase=welcome
          // renders the WelcomePhase inside the workspace shell so the
          // prompt input is available end-to-end.
          href="/workspace#phase=welcome"
          // Clear stale brief/build/plan so the user gets a TRUE fresh
          // start. Without this, the workspace shell would hydrate the
          // previous brief from localStorage and (in the worst case)
          // auto-rebuild it.
          onClick={() => {
            try {
              localStorage.removeItem("pebble.brief");
              localStorage.removeItem("pebble.lastBuild");
              localStorage.removeItem("pebble.plan");
              sessionStorage.removeItem("pebble.autostart");
            } catch { /* storage disabled — fine */ }
          }}
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

function SubNavLink({
  href, Icon, label, active,
}: {
  href: string;
  Icon: IconType;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-2 px-2 py-1.5 rounded-md text-xs font-semibold ${
        active ? "text-primary" : "text-muted-foreground hover:text-foreground"
      }`}
    >
      <Icon className="w-3.5 h-3.5" />
      {label}
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
