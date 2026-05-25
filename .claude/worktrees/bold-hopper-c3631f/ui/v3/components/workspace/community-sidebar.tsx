"use client";

/**
 * CommunitySidebar — dedicated nav for the /community page (and its sub
 * routes: /community/launchpad, /community/hire-a-partner, /community/affiliate).
 *
 * Marc 2026-05-25 reference: the community page has its own context — it's
 * the "Pebble Community Hub" surface — so the sidebar items here are
 * community-themed (Home, Showcase, Launchpad, Partners, Affiliate, Settings)
 * rather than the workspace items (Projects/Templates/Inbox/etc.) that
 * DashboardSidebar carries.
 *
 * Visual style matches DashboardSidebar (glass, vertical nav, bottom-pinned
 * Settings) so the architectural-hero photo bg shows through both rails the
 * same way.
 */

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Image as ImageIcon,
  Rocket,
  Briefcase,
  Gift,
  Settings,
} from "lucide-react";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

type IconType = typeof Home;

export function CommunitySidebar() {
  const pathname = usePathname() || "";

  return (
    <aside className="w-[240px] bg-card/70 backdrop-blur-xl border-r border-border/50 flex flex-col h-full overflow-hidden">
      {/* Brand mark — "Pebble Community Hub" sits in the sidebar header,
          matching the ref. Acts as a back-to-home link. */}
      <div className="px-5 pt-6 pb-5">
        <Link
          href="/community"
          className="inline-flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <span className="w-5 h-5 rounded-full bg-foreground/80 grid place-items-center text-[10px] font-bold text-background">
            P
          </span>
          <span className="text-sm font-bold tracking-tight text-foreground leading-tight">
            Pebble<br />Community Hub
          </span>
        </Link>
      </div>

      {/* Primary nav — community-themed */}
      <nav className="flex-1 px-3 flex flex-col gap-1">
        <NavLink
          href="/community"
          Icon={Home}
          label="Home"
          active={pathname === "/community"}
        />
        <NavLink
          href="/community/launchpad"
          Icon={Rocket}
          label="Launchpad"
          active={pathname.startsWith("/community/launchpad")}
        />
        <NavLink
          href="/community/hire-a-partner"
          Icon={Briefcase}
          label="Hire a Partner"
          active={pathname.startsWith("/community/hire-a-partner")}
        />
        <NavLink
          href="/community/affiliate"
          Icon={Gift}
          label="Affiliate"
          active={pathname.startsWith("/community/affiliate")}
        />
        {/* Showcase points back to /community#showcase — the filmstrip
            section on the main community page. */}
        <NavLink
          href="/community#showcase"
          Icon={ImageIcon}
          label="Showcase"
          active={false}
        />
      </nav>

      {/* Footer — Settings link, pinned bottom */}
      <div className="px-3 pb-5 pt-3 border-t border-border/40 mt-3">
        <NavLink
          href="/settings"
          Icon={Settings}
          label="Settings"
          active={pathname.startsWith("/settings")}
        />
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
          : "text-white/70 hover:bg-white/10 hover:text-white"
      }`}
    >
      <Icon className="w-4 h-4 shrink-0" />
      {label}
    </Link>
  );
}
