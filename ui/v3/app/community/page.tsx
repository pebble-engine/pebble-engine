"use client";

/**
 * /community — Phase 45 (2026-05-22).
 *
 * Landing for the Community section. Three pillars that map to the
 * sub-routes in the dashboard sidebar:
 *
 *   - Launchpad         — gallery of community-shared designs + templates
 *   - Hire a Partner    — directory of designers willing to take work
 *   - Affiliate Program — refer a friend, earn credit (Phase 49+)
 *
 * This is intentionally a stub. The community marketplace is a real
 * pivot in the business model (two-sided marketplace, supply curation,
 * payouts via Stripe Connect, moderation load). Phase 48 NLM critique
 * will pressure-test the pivot before we commit engineering time.
 */

import React from "react";
import Link from "next/link";
import { Compass, Briefcase, Gift } from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

export default function CommunityHomePage() {
  return (
    <DashboardLayout topNavLabel="Community">
      <div className="p-8">
        <div className="max-w-5xl mx-auto space-y-8">
          <div>
            <h1 className={`${type.display.m} text-foreground`}>Community</h1>
            <p className={`${type.body.s} text-muted-foreground mt-1 max-w-xl`}>
              Where Pebble builders meet. Browse what others have shipped,
              hire a designer for a custom job, or earn credit for sending
              friends our way.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Pillar
              href="/community/launchpad"
              Icon={Compass}
              title="Launchpad"
              blurb="Public showcase of designs, templates, and case studies from the Pebble community. Open to all — no plan required to browse."
            />
            <Pillar
              href="/community/hire-a-partner"
              Icon={Briefcase}
              title="Hire a Partner"
              blurb="Need a custom build or design polish? Browse vetted Pebble Partners and reach out directly."
            />
            <Pillar
              href="/community/affiliate"
              Icon={Gift}
              title="Affiliate Program"
              blurb="Refer Pebble to friends and earn account credit on every paid plan they start."
            />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function Pillar({
  href, Icon, title, blurb,
}: {
  href: string;
  Icon: typeof Compass;
  title: string;
  blurb: string;
}) {
  return (
    <Link
      href={href}
      className={`${interactions.card} bg-card border border-border rounded-2xl p-6 flex flex-col gap-3 group`}
    >
      <div className="w-12 h-12 rounded-xl bg-primary/10 text-primary flex items-center justify-center group-hover:scale-105 transition-transform">
        <Icon className="w-6 h-6" />
      </div>
      <div>
        <h2 className={`${type.heading.m} text-foreground`}>{title}</h2>
        <p className={`${type.body.s} text-muted-foreground mt-1 leading-snug`}>{blurb}</p>
      </div>
      <span className={`${type.label} text-primary mt-auto`}>Explore →</span>
    </Link>
  );
}
