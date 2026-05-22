"use client";

/**
 * /community/affiliate — Phase 45 stub.
 *
 * Refer-a-friend with account credit. Mechanism is straightforward
 * (signed referral codes, Stripe coupon issuance, attribution window),
 * but it's a real flow with abuse vectors (self-referral, throwaway
 * accounts) so we won't ship it half-baked.
 *
 * Stub today, wait-list email; build in Phase 49+.
 */

import React from "react";
import Link from "next/link";
import { Gift, Mail } from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

export default function AffiliatePage() {
  return (
    <DashboardLayout topNavLabel="Affiliate Program">
      <div className="p-8">
        <div className="max-w-3xl mx-auto space-y-6 text-center pt-16">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-primary/10 text-primary items-center justify-center mx-auto">
            <Gift className="w-7 h-7" />
          </div>
          <h1 className={`${type.display.l} text-foreground`}>Affiliate program — in design.</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-xl mx-auto`}>
            Refer Pebble to a friend or client and earn account credit toward
            your plan when they upgrade. Simple, no third-party tracker, paid
            out as a credit to your subscription — not a check we mail twice
            a year.
          </p>
          <p className={`${type.body.s} text-muted-foreground max-w-lg mx-auto`}>
            We&apos;re finalizing the payout terms (typical industry rate is
            20-30% of first-year revenue). Want first crack at it when it
            launches? Email us and we&apos;ll save you a spot.
          </p>
          <div className="flex gap-3 justify-center pt-4 flex-wrap">
            <Link
              href="mailto:hello@pebbleapp.ai?subject=Pebble%20Affiliate%20Early%20Access"
              className={`${interactions.button} inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-bold`}
            >
              <Mail className="w-4 h-4" />
              Get early access
            </Link>
            <Link
              href="/community"
              className={`${interactions.chip} inline-flex items-center bg-card border border-border text-foreground px-5 py-2.5 rounded-full text-sm font-semibold`}
            >
              Back to Community
            </Link>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
