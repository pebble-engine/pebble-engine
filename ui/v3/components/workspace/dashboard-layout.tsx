"use client";

/**
 * DashboardLayout — Phase 45 (2026-05-22).
 *
 * Wraps the TopNav + DashboardSidebar + page slot for every "logged-in
 * workspace" surface (dashboard, integrations, community/*). Lets each
 * page focus on its main-area content without rebuilding chrome.
 *
 * Why not a Next.js layout.tsx file
 * ---------------------------------
 * App-router layouts apply to *every* route under a folder. /dashboard
 * and /integrations live at different paths — making this a real Next
 * layout would require nesting them under a /(workspace)/ route group,
 * which churns 5+ files and breaks existing deep links. Component
 * wrapper is two lines per page and zero new routes. Revisit when we
 * actually have 6+ workspace pages.
 */

import React from "react";
import { TopNav } from "@/components/top-nav";
import { DashboardSidebar } from "./dashboard-sidebar";

export function DashboardLayout({
  topNavLabel = "Workspace",
  children,
}: {
  /** Project-name slot on the TopNav. Defaults to "Workspace" for the
      dashboard pages; individual pages can override with something more
      specific (e.g. "Integrations"). */
  topNavLabel?: string;
  children: React.ReactNode;
}) {
  return (
    <div data-workspace-theme="mono" className="min-h-screen-safe flex flex-col">
      <TopNav projectName={topNavLabel} />
      <div className="flex flex-1">
        <DashboardSidebar />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
