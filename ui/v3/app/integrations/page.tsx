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
  Plus,
} from "lucide-react";
import { TopNav } from "@/components/top-nav";
import { ControlCenter } from "@/components/control-center";
import { DashboardSidebar } from "@/components/workspace/dashboard-sidebar";
import { NotificationBell } from "@/components/notification-bell";
import { BRAND_IDENTITY } from "@/components/brand-marks";
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
    "On Integrations. Ask me how to connect any of these to your project, or I'll take you to the right setup page.";

  return (
    <div className="flex flex-col h-screen-safe">
      <TopNav projectName="Integrations" rightSlot={topRightSlot} />
      <div className="flex-1 min-h-0">
        <ControlCenter greeting={greeting} leftSidebar={<DashboardSidebar />}>
          <div className="p-6 md:p-8">
            <div className="max-w-5xl mx-auto space-y-10">
              <header className="space-y-1">
                <p className="text-sm font-semibold text-muted-foreground">Integrations</p>
                <h1 className={`${type.display.m} text-foreground`}>Connect the tools you already use.</h1>
                <p className={`${type.body.s} text-muted-foreground max-w-xl`}>
                  Payments, email, analytics, scheduling — wire them up once and they
                  work everywhere your site does.
                </p>
              </header>

              {groupOrder.filter((g) => grouped[g]).map((group) => (
                <section key={group} className="space-y-4">
                  <div className="flex items-baseline justify-between gap-3">
                    <h2 className={`${type.heading.l} text-foreground`}>{group}</h2>
                    <p className={type.caption}>
                      {grouped[group].length} {grouped[group].length === 1 ? "integration" : "integrations"}
                    </p>
                  </div>
                  {/* 2-up on md+ — bigger, brand-colored cards (per Marc's
                      "too many boxes" feedback). Each card is wider, taller,
                      and uses the vendor's actual color so users get the
                      same brand-recognition effect McDonald's red gets. */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </ControlCenter>
      </div>
    </div>
  );
}

function IntegrationCard({ item }: { item: Integration }) {
  const Icon = item.icon;
  const identity = BRAND_IDENTITY[item.name];
  const bg = identity?.bg ?? "#1f2937";
  // Mailchimp yellow / Supabase green / Mailchimp etc. read as light
  // colors — they need dark text. Hard-coded list rather than
  // attempting brightness math because we only have 10 vendors and
  // human judgment beats a contrast calc here.
  const lightBg = item.name === "Mailchimp" || item.name === "Supabase" || item.name === "Google Analytics";
  const onColorText = lightBg ? "text-black/90" : "text-white";
  const onColorMuted = lightBg ? "text-black/60" : "text-white/70";
  const BrandMark = identity?.Mark;

  return (
    <div className={`${interactions.card} relative overflow-hidden rounded-2xl border border-border bg-card flex flex-col md:flex-row`}>
      {/* LEFT — brand-colored swatch with the company glyph. The
          background uses the vendor's actual brand color so the card
          reads as recognizable at a glance the same way McDonald's
          red does. Glyph sits behind everything at low opacity so the
          icon is felt more than read. */}
      <div
        className="relative md:w-[180px] shrink-0 p-6 flex flex-col justify-between overflow-hidden"
        style={{ backgroundColor: bg }}
      >
        {/* Soft radial highlight + giant brand glyph as backdrop */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background: `radial-gradient(circle at 30% 0%, rgba(255,255,255,0.15), transparent 60%)`,
          }}
        />
        {BrandMark && (
          <BrandMark
            className={`pointer-events-none absolute -bottom-6 -right-6 w-32 h-32 ${onColorText} opacity-15`}
          />
        )}
        <div className="relative flex items-start justify-between gap-3">
          <div className={`w-10 h-10 rounded-lg ${lightBg ? "bg-black/10" : "bg-white/15"} backdrop-blur-sm flex items-center justify-center ${onColorText}`}>
            <Icon className="w-5 h-5" />
          </div>
          <StatusBadge status={item.status} onColor={lightBg ? "dark" : "light"} />
        </div>
        <div className="relative mt-6">
          <p className={`${type.mono} text-[10px] uppercase tracking-widest ${onColorMuted}`}>
            {item.group}
          </p>
          <h3 className={`text-lg font-bold ${onColorText} leading-tight mt-0.5`}>{item.name}</h3>
        </div>
      </div>

      {/* RIGHT — content + resource links + status action */}
      <div className="flex-1 p-5 flex flex-col gap-3 min-w-0">
        <p className={`${type.body.s} text-muted-foreground leading-snug`}>{item.blurb}</p>

        {item.pebbleTutorialUrl && (
          <Link
            href={item.pebbleTutorialUrl}
            className={`${interactions.chip} inline-flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-semibold bg-primary/10 text-primary hover:bg-primary/20 transition-colors w-fit`}
          >
            <BookOpen className="w-4 h-4" />
            Pebble walkthrough
          </Link>
        )}

        {(item.docsUrl || item.youtubeUrl || item.companyUrl) && (
          <div className="flex items-center gap-1.5 flex-wrap">
            {item.docsUrl     && <ResourceLink href={item.docsUrl}     Icon={BookOpen}    label="Docs"  />}
            {item.youtubeUrl  && <ResourceLink href={item.youtubeUrl}  Icon={PlayCircle}  label="Video" />}
            {item.companyUrl  && <ResourceLink href={item.companyUrl}  Icon={Globe}       label="Visit" />}
          </div>
        )}

        <div className="pt-1 mt-auto">
          {item.status === "live" && (
            <span className={`${type.label} text-spark-deep inline-flex items-center gap-1.5`}>
              <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500" /> Working in your projects
            </span>
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
              className={`${interactions.button} inline-flex items-center justify-center gap-2 bg-primary/10 text-primary border border-primary/30 px-4 py-2 rounded-lg text-sm font-semibold w-fit`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              Builder plan
            </Link>
          )}
        </div>
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

function StatusBadge({ status, onColor = "default" }: { status: Status; onColor?: "default" | "light" | "dark" }) {
  // Brand-colored swatches need a higher-contrast badge that reads on
  // top of the vendor color (light text on dark bg, dark text on
  // light bg). `default` = the original muted treatment for plain
  // backgrounds.
  if (onColor === "light") {
    // Card background is dark — render light badge.
    if (status === "live") {
      return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-emerald-400/90 text-emerald-950">Live</span>;
    }
    if (status === "connect") {
      return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-white/20 text-white border border-white/30">Soon</span>;
    }
    return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-white/20 text-white border border-white/30">Paid plan</span>;
  }
  if (onColor === "dark") {
    // Card background is light (Mailchimp yellow, Supabase green) — render dark badge.
    if (status === "live") {
      return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-emerald-900/90 text-emerald-50">Live</span>;
    }
    if (status === "connect") {
      return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-black/15 text-black/80 border border-black/20">Soon</span>;
    }
    return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-black/15 text-black/80 border border-black/20">Paid plan</span>;
  }
  // Default (no brand backdrop)
  if (status === "live") {
    return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-spark/10 text-spark-deep border border-spark/30">Live</span>;
  }
  if (status === "connect") {
    return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-muted text-muted-foreground border border-border">Soon</span>;
  }
  return <span className="text-[10px] font-bold uppercase tracking-widest px-2 py-1 rounded-full bg-primary/10 text-primary border border-primary/30">Paid plan</span>;
}
