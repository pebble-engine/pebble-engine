"use client";

/**
 * /community/launchpad — Phase 45 stub.
 *
 * Community showcase: designs other builders chose to share publicly.
 * Long-term this is a curated gallery (think Dribbble for Pebble sites).
 * Today it's a stub that explains the concept and an early-access wait-
 * list — supply side ramps with template marketplace in a later phase.
 */

import React from "react";
import Link from "next/link";
import { Compass, Sparkles } from "lucide-react";
import { DashboardLayout } from "@/components/workspace/dashboard-layout";
import { type } from "@/lib/type";
import { interactions } from "@/lib/interactions";

export default function LaunchpadPage() {
  return (
    <DashboardLayout topNavLabel="Launchpad">
      <div className="p-8">
        <div className="max-w-3xl mx-auto space-y-6 text-center pt-16">
          <div className="inline-flex w-16 h-16 rounded-2xl bg-primary/10 text-primary items-center justify-center mx-auto">
            <Compass className="w-7 h-7" />
          </div>
          <h1 className={`${type.display.l} text-foreground`}>Launchpad is on the runway.</h1>
          <p className={`${type.body.m} text-muted-foreground max-w-xl mx-auto`}>
            A public gallery where Pebble builders showcase what they shipped —
            with the build story, the DNA they used, and a one-click "remix this"
            button so anyone can start from someone else&apos;s great work.
          </p>
          <p className={`${type.body.s} text-muted-foreground max-w-lg mx-auto`}>
            We&apos;re wiring this up alongside the template marketplace. If you&apos;ve
            built something you&apos;re proud of and want to share it, just publish
            it for now — we&apos;ll pull from your live sites when Launchpad opens.
          </p>
          <div className="flex gap-3 justify-center pt-4 flex-wrap">
            <Link
              href="/"
              className={`${interactions.button} inline-flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-full text-sm font-bold`}
            >
              <Sparkles className="w-4 h-4" />
              Build something to share
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
