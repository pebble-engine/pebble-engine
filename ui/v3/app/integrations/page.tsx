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
} from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

type Status = "live" | "connect" | "paid";

type Integration = {
  name:        string;
  blurb:       string;
  icon:        typeof CreditCard;
  status:      Status;
  group:       string;
  href?:       string;
};

const INTEGRATIONS: Integration[] = [
  // ── Payments ────────────────────────────────────────────────────────────
  {
    name:   "Stripe Payments",
    blurb:  "Take card payments on your site — products, services, deposits.",
    icon:   CreditCard,
    status: "paid",
    group:  "Payments",
  },
  // ── Email ───────────────────────────────────────────────────────────────
  {
    name:   "Resend",
    blurb:  "Reliable transactional email for form replies + auto-responders.",
    icon:   Mail,
    status: "live",
    group:  "Email",
  },
  {
    name:   "Mailchimp",
    blurb:  "Sync newsletter signups straight into your Mailchimp audience.",
    icon:   Megaphone,
    status: "paid",
    group:  "Email",
  },
  // ── Analytics ───────────────────────────────────────────────────────────
  {
    name:   "Plausible Analytics",
    blurb:  "Cookieless page-view tracking, included on every site.",
    icon:   BarChart3,
    status: "live",
    group:  "Analytics",
  },
  {
    name:   "Google Analytics",
    blurb:  "Add your GA4 tag for cross-property reporting.",
    icon:   BarChart3,
    status: "connect",
    group:  "Analytics",
  },
  // ── Bookings ────────────────────────────────────────────────────────────
  {
    name:   "Calendly",
    blurb:  "Embed your booking page so visitors can self-schedule.",
    icon:   Calendar,
    status: "paid",
    group:  "Bookings",
  },
  // ── Comms ───────────────────────────────────────────────────────────────
  {
    name:   "Slack",
    blurb:  "Get pinged in Slack when someone fills out your contact form.",
    icon:   MessageSquare,
    status: "paid",
    group:  "Communication",
  },
  // ── Data / storage ──────────────────────────────────────────────────────
  {
    name:   "Supabase",
    blurb:  "Auth + storage that powers your Pebble account.",
    icon:   Database,
    status: "live",
    group:  "Platform",
  },
  // ── Automation ──────────────────────────────────────────────────────────
  {
    name:   "Zapier",
    blurb:  "Send form submissions to 5,000+ apps via Zapier webhooks.",
    icon:   Zap,
    status: "paid",
    group:  "Automation",
  },
  {
    name:   "Custom webhook",
    blurb:  "POST form data to any URL — already shipped for every project.",
    icon:   Workflow,
    status: "live",
    group:  "Automation",
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
