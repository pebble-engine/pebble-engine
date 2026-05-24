"use client";

/**
 * /integrations — Phase 45 (2026-05-22).
 *
 * Inspired by Base44's integrations panel. We show the connectors Pebble
 * supports (or will support) grouped by what they DO for the customer's
 * site, not by vendor. Each card has one of three states:
 *
 *   - "Live"       — already wired and usable today (Stripe billing,
 *                    Resend transactional, Plausible analytics)
 *   - "Connect"    — stub; will be wired in a follow-up phase
 *   - "Paid plan"  — gated behind Builder/Pro tier
 *
 * Marc said "We will configure all buttons and layouts next." so the
 * cards are deliberately stubs — no OAuth flows, no popups, no fake
 * "Connected ✓" lies. Click-through to a coming-soon notice or pricing
 * page. The point of this Phase is the SHELL, not the wiring.
 */

import React from "react";
import Link from "next/link";
import {
  CreditCard,
  Mail,
  BarChart3,
  Calendar,
  Megaphone,
  MessageSquare,
  Database,
  Workflow,
  Zap,
  Sparkles,
  BookOpen,
  PlayCircle,
  Globe,
  ExternalLink,
} from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

type Status = "live" | "connect" | "paid";

// 2026-05-23: every integration carries the three external links Marc
// asked for — a docs link (company-authored, the source of truth), a
// YouTube link (the company's own intro / setup video where one exists,
// for visual learners), and a homepage link. Optional Pebble tutorial
// URL covers cases where we need our own walkthrough on top.
type Integration = {
  name:               string;
  blurb:              string;
  icon:               typeof CreditCard;
  status:             Status;
  group:              string;
  href?:              string;
  /** Company homepage. */
  companyUrl?:        string;
  /** Company-authored documentation. */
  docsUrl?:           string;
  /** Company-authored YouTube video (must be the vendor's official
   *  channel — don't link third-party "how to set up X" videos). */
  youtubeUrl?:        string;
  /** In-app Pebble walkthrough for connecting this integration. */
  pebbleTutorialUrl?: string;
};

const INTEGRATIONS: Integration[] = [
  // ── Payments ────────────────────────────────────────────────────────────
  {
    name:       "Stripe Payments",
    blurb:      "Take card payments on your site — products, services, deposits.",
    icon:       CreditCard,
    status:     "paid",
    group:      "Payments",
    companyUrl: "https://stripe.com",
    docsUrl:    "https://stripe.com/docs",
    youtubeUrl: "https://www.youtube.com/@StripeDevelopers",
  },
  // ── Email ───────────────────────────────────────────────────────────────
  {
    name:       "Resend",
    blurb:      "Reliable transactional email for form replies + auto-responders.",
    icon:       Mail,
    status:     "live",
    group:      "Email",
    companyUrl: "https://resend.com",
    docsUrl:    "https://resend.com/docs",
    youtubeUrl: "https://www.youtube.com/@resendhq",
  },
  {
    name:       "Mailchimp",
    blurb:      "Sync newsletter signups straight into your Mailchimp audience.",
    icon:       Megaphone,
    status:     "paid",
    group:      "Email",
    companyUrl: "https://mailchimp.com",
    docsUrl:    "https://mailchimp.com/help/",
    youtubeUrl: "https://www.youtube.com/@Mailchimp",
  },
  // ── Analytics ───────────────────────────────────────────────────────────
  {
    name:       "Plausible Analytics",
    blurb:      "Cookieless page-view tracking, included on every site.",
    icon:       BarChart3,
    status:     "live",
    group:      "Analytics",
    companyUrl: "https://plausible.io",
    docsUrl:    "https://plausible.io/docs",
  },
  {
    name:       "Google Analytics",
    blurb:      "Add your GA4 tag for cross-property reporting.",
    icon:       BarChart3,
    status:     "connect",
    group:      "Analytics",
    companyUrl: "https://analytics.google.com",
    docsUrl:    "https://support.google.com/analytics",
    youtubeUrl: "https://www.youtube.com/@googleanalytics",
  },
  // ── Bookings ────────────────────────────────────────────────────────────
  {
    name:       "Calendly",
    blurb:      "Embed your booking page so visitors can self-schedule.",
    icon:       Calendar,
    status:     "paid",
    group:      "Bookings",
    companyUrl: "https://calendly.com",
    docsUrl:    "https://help.calendly.com",
    youtubeUrl: "https://www.youtube.com/@Calendly",
  },
  // ── Comms ───────────────────────────────────────────────────────────────
  {
    name:       "Slack",
    blurb:      "Get pinged in Slack when someone fills out your contact form.",
    icon:       MessageSquare,
    status:     "paid",
    group:      "Communication",
    companyUrl: "https://slack.com",
    docsUrl:    "https://slack.com/help",
    youtubeUrl: "https://www.youtube.com/@SlackHQ",
  },
  // ── Data / storage ──────────────────────────────────────────────────────
  {
    name:       "Supabase",
    blurb:      "Auth + storage that powers your Pebble account.",
    icon:       Database,
    status:     "live",
    group:      "Platform",
    companyUrl: "https://supabase.com",
    docsUrl:    "https://supabase.com/docs",
    youtubeUrl: "https://www.youtube.com/@Supabase",
  },
  // ── Automation ──────────────────────────────────────────────────────────
  {
    name:       "Zapier",
    blurb:      "Send form submissions to 5,000+ apps via Zapier webhooks.",
    icon:       Zap,
    status:     "paid",
    group:      "Automation",
    companyUrl: "https://zapier.com",
    docsUrl:    "https://help.zapier.com",
    youtubeUrl: "https://www.youtube.com/@zapier",
  },
  {
    name:       "Custom webhook",
    blurb:      "POST form data to any URL — already shipped for every project.",
    icon:       Workflow,
    status:     "live",
    group:      "Automation",
    // Pebble feature, not a vendor — only the in-app guide makes sense.
    pebbleTutorialUrl: "/help/webhooks",
  },
];

export default function IntegrationsPage() {
  // Group by category for the rendered sections.
  const grouped = INTEGRATIONS.reduce<Record<string, Integration[]>>((acc, i) => {
    (acc[i.group] ||= []).push(i);
    return acc;
  }, {});
  const groupOrder = ["Payments", "Email", "Analytics", "Bookings", "Communication", "Automation", "Platform"];

  return (
    <DashboardLayout topNavLabel="Integrations">
      <div className="p-8">
        <div className="max-w-5xl mx-auto space-y-8">
          <div>
            <h1 className={`${type.display.m} text-foreground`}>Integrations</h1>
            <p className={`${type.body.s} text-muted-foreground mt-1 max-w-xl`}>
              Connect your Pebble site to the services that actually run your
              business. Payments, email, analytics, scheduling — wire them up
              once and they work everywhere.
            </p>
          </div>

          {groupOrder.filter((g) => grouped[g]).map((group) => (
            <section key={group} className="space-y-3">
              <h2 className={`${type.eyebrow}`}>{group}</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {grouped[group].map((it) => (
                  <IntegrationCard key={it.name} item={it} />
                ))}
              </div>
            </section>
          ))}

          {/* Honest footer — we don't claim "47 integrations" when we
              have 3 live. Sets expectation that this list grows by ship-
              ping real wiring, not by ballooning the catalog. */}
          <p className={`${type.caption} pt-4 border-t border-border`}>
            We add integrations one at a time, only after they actually work end-to-end.
            Have one you need? <Link href="/help" className="text-primary hover:underline">Tell us</Link>.
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}

function IntegrationCard({ item }: { item: Integration }) {
  const Icon = item.icon;
  const hasResources =
    !!(item.companyUrl || item.docsUrl || item.youtubeUrl || item.pebbleTutorialUrl);
  return (
    <div
      className={`${interactions.card} bg-card border border-border rounded-2xl p-5 flex flex-col gap-3`}
    >
      <div className="flex items-center justify-between">
        <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center">
          <Icon className="w-5 h-5" />
        </div>
        <StatusBadge status={item.status} />
      </div>
      <div>
        <h3 className={`${type.heading.m} text-foreground`}>{item.name}</h3>
        <p className={`${type.body.s} text-muted-foreground mt-1 leading-snug`}>{item.blurb}</p>
      </div>

      {/* Resource links row — Marc's 2026-05-23 brief: each integration
          should give the user three ways in (docs / video / website)
          so visual learners and reference-checkers both have something
          to click. Tutorial link surfaces above the status action when
          present (Pebble-authored walkthrough is the most useful one
          since it's contextual to your project). */}
      {item.pebbleTutorialUrl && (
        <Link
          href={item.pebbleTutorialUrl}
          className={`${interactions.chip} inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold bg-primary/10 text-primary hover:bg-primary/20 transition-colors`}
        >
          <BookOpen className="w-4 h-4" />
          Pebble walkthrough
        </Link>
      )}
      {hasResources && (
        <div className="flex items-center gap-1.5 flex-wrap">
          {item.docsUrl && (
            <ResourceLink href={item.docsUrl} Icon={BookOpen} label="Docs" />
          )}
          {item.youtubeUrl && (
            <ResourceLink href={item.youtubeUrl} Icon={PlayCircle} label="Video" />
          )}
          {item.companyUrl && (
            <ResourceLink href={item.companyUrl} Icon={Globe} label="Visit" />
          )}
        </div>
      )}

      <div className="pt-2 mt-auto">
        {item.status === "live" && (
          <span className={`${type.label} text-spark-deep`}>● Working in your projects</span>
        )}
        {item.status === "connect" && (
          <button
            className={`${interactions.button} bg-card border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold w-full`}
          >
            Connect (coming soon)
          </button>
        )}
        {item.status === "paid" && (
          <Link
            href="/pricing"
            className={`${interactions.button} flex items-center justify-center gap-2 bg-primary/10 text-primary border border-primary/30 px-4 py-2 rounded-lg text-sm font-semibold`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Builder plan
          </Link>
        )}
      </div>
    </div>
  );
}

function ResourceLink({
  href, Icon, label,
}: {
  href: string;
  Icon: typeof BookOpen;
  label: string;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`${interactions.chip} inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-semibold text-muted-foreground hover:text-foreground hover:bg-accent transition-colors border border-border`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>{label}</span>
      <ExternalLink className="w-3 h-3 opacity-60" />
    </a>
  );
}

function StatusBadge({ status }: { status: Status }) {
  if (status === "live") {
    return (
      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-spark/10 text-spark-deep border border-spark/30">
        Live
      </span>
    );
  }
  if (status === "connect") {
    return (
      <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-muted text-muted-foreground border border-border">
        Soon
      </span>
    );
  }
  return (
    <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">
      Paid plan
    </span>
  );
}
