"use client";

/**
 * DashboardSidebar — Marc 2026-05-25 simplified.
 *
 * Stripped to match the design ref: Pebble. wordmark at top, five primary
 * nav items, bottom-pinned Help + Free Plan badge. No more Favorites /
 * Recents drawers, no inline Ask Pebble button (the floating chat widget
 * provides that). Glassmorphism preserved so the community-page photo
 * background can show through.
 *
 * What used to live here that we removed:
 *  - "Your workspace" header (the wordmark replaces it)
 *  - Favorites drawer (the dashboard hero is the primary fresh-user surface)
 *  - Recents drawer (same)
 *  - Inline Ask Pebble button (FloatingPeblet covers this)
 *  - Resources dropdown (Community Hub on its own line below; rest are
 *    discoverable via the community page itself)
 *  - "Start something new" footer CTA (covered by the dashboard hero's
 *    primary button when on /dashboard)
 *
 * The `plan` prop is preserved as an unused option for forward-compat
 * with workspace-shell callers.
 */

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FolderOpen,
  LayoutGrid,
  Inbox,
  Settings,
  HelpCircle,
  Circle,
} from "lucide-react";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";
import {
  listProjects,
  fetchSubscription,
  type ProjectSummary,
  type SubscriptionState,
} from "@/lib/api";

type IconType = typeof FolderOpen;

// Accepts an optional `plan` prop for forward-compat with workspace-shell.
// Currently unused here but preserved so existing callers don't break.
export function DashboardSidebar(_props: { plan?: unknown } = {}) {
  const pathname = usePathname() || "";
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [subscription, setSubscription] = useState<SubscriptionState | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [p, s] = await Promise.all([
          listProjects().catch(() => ({ projects: [] })),
          fetchSubscription().catch(() => null),
        ]);
        setProjects(p.projects || []);
        setSubscription(s);
      } catch {
        // Sidebar should never block the page on a network error.
      }
    })();
  }, []);

  // FREE_LIMIT mirrors pebble/user_plan.py PLAN_LIMITS["free"]["published_sites"].
  const created = projects.length;
  const FREE_LIMIT = 1;
  const atLimit = created >= FREE_LIMIT;
  const isFree = subscription !== null && !subscription?.plan;

  return (
    <aside className="w-[240px] bg-card/70 backdrop-blur-xl border-r border-border/50 flex flex-col h-full overflow-hidden">
      {/* Brand mark — Pebble. wordmark sits at the top, matching the ref */}
      <div className="px-5 pt-6 pb-5">
        <Link
          href="/dashboard"
          className="inline-flex items-baseline gap-0.5 text-2xl font-bold tracking-tight text-foreground hover:opacity-90 transition-opacity"
        >
          Pebble<span className="text-foreground/60">.</span>
        </Link>
      </div>

      {/* Primary nav — five items, vertical */}
      <nav className="flex-1 px-3 flex flex-col gap-1">
        <NavLink
          href="/dashboard"
          Icon={FolderOpen}
          label="Projects"
          active={pathname === "/dashboard" || pathname === "/"}
        />
        <NavLink
          href="/templates"
          Icon={LayoutGrid}
          label="Templates"
          active={pathname.startsWith("/templates")}
        />
        <NavLink
          href="/inbox"
          Icon={Inbox}
          label="Inbox"
          active={pathname.startsWith("/inbox")}
        />
        <NavLink
          href="/settings"
          Icon={Settings}
          label="Settings"
          active={pathname.startsWith("/settings")}
        />
        <NavLink
          href="/help"
          Icon={HelpCircle}
          label="Help"
          active={pathname.startsWith("/help")}
        />
      </nav>

      {/* Footer — Help quick-link + Free Plan badge, pinned bottom */}
      <div className="px-3 pb-5 pt-3 space-y-1 border-t border-border/40 mt-3">
        <NavLink
          href="/help"
          Icon={HelpCircle}
          label="Help"
          active={false}
        />
        {isFree && (
          <Link
            href={atLimit ? "/pricing" : "/dashboard"}
            className={`${interactions.chip} flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium ${
              atLimit
                ? "text-destructive hover:bg-destructive/10"
                : "text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
            title={atLimit ? `${created} / ${FREE_LIMIT} — upgrade for more` : `${created} / ${FREE_LIMIT} projects`}
          >
            <Circle className={`w-3.5 h-3.5 ${atLimit ? "fill-destructive text-destructive" : "fill-emerald-500/40 text-emerald-500/60"}`} />
            Free Plan
          </Link>
        )}
      </div>
    </aside>
  );
}

// ---------------------------------------------------------------------------

function NavLink({
  href,
  Icon,
  label,
  active,
}: {
  href: string;
  Icon: IconType;
  label: string;
  active: boolean;
}) {
  return (
    <Link
      href={href}
      className={`${interactions.chip} flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium ${
        active
          ? "bg-foreground/10 text-foreground"
          : "text-muted-foreground hover:bg-card hover:text-foreground"
      }`}
    >
      <Icon className="w-4 h-4 shrink-0" />
      {label}
    </Link>
  );
}
