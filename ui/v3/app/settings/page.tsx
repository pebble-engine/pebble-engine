"use client";

/**
 * /settings — multi-tab account management.
 *
 * Five tabs:
 *   Profile  — display name, timezone, avatar, email + email-change form (A4)
 *   Security — password change with re-auth challenge (A2)
 *   Billing  — plan, next charge, Stripe portal link
 *   Activity — placeholder; B2 wires /api/account/activity
 *   Data     — delete account (A3 flow) + export placeholder (B3)
 *
 * Auth: redirects to /login if no signed-in user.
 */

import { Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Settings as SettingsIcon } from "lucide-react";
import { type } from "@/lib/type";
import { TopNav } from "@/components/top-nav";
import { useAuth } from "@/components/auth-provider";
import { ProfileTab } from "@/components/settings/profile-tab";
import { SecurityTab } from "@/components/settings/security-tab";
import { BillingTab } from "@/components/settings/billing-tab";
import { ActivityTab } from "@/components/settings/activity-tab";
import { DataTab } from "@/components/settings/data-tab";

// ── tab config ─────────────────────────────────────────────────────────────────

const TABS = [
  { value: "profile",  label: "Profile" },
  { value: "security", label: "Security" },
  { value: "billing",  label: "Billing" },
  { value: "activity", label: "Activity" },
  { value: "data",     label: "Data" },
] as const;

type TabValue = typeof TABS[number]["value"];

// ── main component ────────────────────────────────────────────────────────────

function SettingsPageContent() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [active, setActive] = useState<TabValue>("profile");

  // ── auth redirect ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!loading && !user) router.replace("/login?next=/settings");
  }, [loading, user, router]);

  // ── shimmer ────────────────────────────────────────────────────────────────
  if (loading || !user) {
    return (
      <div className="min-h-screen-safe flex flex-col">
        <TopNav projectName="Settings" />
        <main className="flex-1 px-6 py-12">
          <div className="max-w-3xl mx-auto">
            <div className="h-8 w-40 bg-muted rounded animate-pulse mb-8" />
            <div className="h-32 bg-muted/50 rounded-2xl animate-pulse" />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen-safe flex flex-col">
      <TopNav projectName="Settings" />

      <main className="flex-1 px-6 py-12 md:py-16">
        <div className="mx-auto max-w-3xl">

          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }} className="space-y-3 mb-8"
          >
            <div className="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center">
              <SettingsIcon className="w-6 h-6" />
            </div>
            <h1 className={`${type.dashboard.display.m} text-foreground`}>
              Settings
            </h1>
            <p className="text-muted-foreground text-sm">
              Manage your account, security, billing, and data preferences.
            </p>
          </motion.div>

          {/* Tab nav */}
          <div className="mb-8 flex gap-1 border-b border-border">
            {TABS.map((t) => (
              <button
                key={t.value}
                onClick={() => setActive(t.value)}
                className={`px-4 py-2 text-sm transition-colors ${
                  active === t.value
                    ? "border-b-2 border-foreground font-medium text-foreground"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {active === "profile"  && <ProfileTab />}
          {active === "security" && <SecurityTab />}
          {active === "billing"  && <BillingTab />}
          {active === "activity" && <ActivityTab />}
          {active === "data"     && <DataTab />}

        </div>
      </main>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen-safe bg-background" />}>
      <SettingsPageContent />
    </Suspense>
  );
}
