"use client";

/**
 * /community/hire-a-partner — Phase 45 stub.
 *
 * Designer marketplace. Real implementation needs Stripe Connect for
 * payouts, KYC/tax for designers, moderation, refund flows, dispute
 * handling. That's a quarter+ of work — Phase 48 NLM critique will
 * pressure-test before we commit.
 *
 * For now: a stub that lets designers self-nominate via a simple form
 * link (Marc handles applications by hand for the first 5-10 partners).
 */

import React from "react";
import Link from "next/link";
import { Briefcase, Mail } from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { CommunitySidebar } from "@/components/workspace/community-sidebar";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

export default function HirePartnerPage() {
  return (
    <DashboardLayout topNavLabel="Hire a Partner" sidebar={<CommunitySidebar />}>
      <div className="p-8">
        <div className="max-w-3xl mx-auto space-y-6 text-center pt-16">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-primary/10 text-primary items-center justify-center mx-auto">
            <Briefcase className="w-7 h-7" />
          </div>
          <h1 className={`${type.dashboard.display.l} text-foreground`}>Pebble Partners — coming soon.</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-xl mx-auto`}>
            A directory of designers and developers willing to take on custom
            Pebble work: brand refreshes, copy polish, integrations setup,
            multi-page builds. You browse profiles, message directly, agree on
            a price, and we stay out of your way.
          </p>
          <p className={`${type.body.s} text-muted-foreground max-w-lg mx-auto`}>
            For now: if you need a partner, email us and we&apos;ll match you
            with someone we trust. If you ARE a designer who wants to be
            listed, send us your portfolio.
          </p>
          <div className="flex gap-3 justify-center pt-4 flex-wrap">
            <Link
              href="mailto:hello@pebbleapp.ai?subject=Hire%20a%20Pebble%20Partner"
              className={`${interactions.button} inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-bold`}
            >
              <Mail className="w-4 h-4" />
              Get matched
            </Link>
            <Link
              href="mailto:hello@pebbleapp.ai?subject=Become%20a%20Pebble%20Partner"
              className={`${interactions.chip} inline-flex items-center bg-card border border-border text-foreground px-5 py-2.5 rounded-full text-sm font-semibold`}
            >
              Apply to be a Partner
            </Link>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
