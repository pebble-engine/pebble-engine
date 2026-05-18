"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Check, Minus, X } from "lucide-react";
import { AuthMenu } from "@/components/auth-menu";
import { useAuth } from "@/components/auth-provider";
import { createCheckoutSession, fetchSubscription, type SubscriptionState } from "@/lib/api";

// ── Plan definitions ──────────────────────────────────────────────────────────

type PlanKey = "free" | "starter" | "pro";

const PLANS: Record<PlanKey, {
  name: string;
  price: string;
  period: string;
  description: string;
  featured: boolean;
  cta: string;
  stripePlan?: "starter" | "pro";
}> = {
  free: {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Build your first site and see what Pebble can do. No card needed.",
    featured: false,
    cta: "Start building",
  },
  starter: {
    name: "Starter",
    price: "$29",
    period: "/month",
    description: "For individuals and small businesses ready to go live.",
    featured: true,
    cta: "Get Starter",
    stripePlan: "starter",
  },
  pro: {
    name: "Pro",
    price: "$59",
    period: "/month",
    description: "For businesses that need multi-page sites and all the extras.",
    featured: false,
    cta: "Get Pro",
    stripePlan: "pro",
  },
};

// ── Feature comparison table ──────────────────────────────────────────────────

type CellValue = boolean | string;

interface FeatureRow {
  label: string;
  free: CellValue;
  starter: CellValue;
  pro: CellValue;
  note?: string;
}

interface CategoryRow {
  category: string;
}

type TableRow = FeatureRow | CategoryRow;

const TABLE: TableRow[] = [
  { category: "Sites & Publishing" },
  { label: "AI site generation",              free: true,        starter: true,        pro: true },
  { label: "Published sites",                 free: "2",         starter: "Unlimited", pro: "Unlimited" },
  { label: "Free Pebble URL (*.pebble.app)",  free: true,        starter: true,        pro: true },
  { label: "Custom domain (yourname.com)",    free: false,       starter: true,        pro: true },

  { category: "Editing" },
  { label: "Click-to-edit visual editor",             free: true,  starter: true,  pro: true },
  { label: "Color palette & style swaps",             free: true,  starter: true,  pro: true },
  { label: "AI tone refinements (friendlier, formal)", free: false, starter: true,  pro: true },
  { label: "Undo / version history",                  free: true,  starter: true,  pro: true },

  { category: "Content" },
  { label: "Single-page sites",                 free: true,  starter: true,  pro: true },
  { label: "Multi-page sites (FAQ, About, …)",  free: false, starter: false, pro: true },
  { label: "Drop-in section library",           free: false, starter: false, pro: true },

  { category: "Forms & Analytics" },
  { label: "Contact form on every site",   free: true,  starter: true,  pro: true },
  { label: "Form submissions inbox",       free: false, starter: true,  pro: true },
  { label: "Site analytics (7-day)",       free: false, starter: true,  pro: true },

  { category: "Support" },
  { label: "Community support",       free: true,  starter: true,  pro: true },
  { label: "Priority email support",  free: false, starter: false, pro: true },
];

const FAQ = [
  {
    q: "Can I cancel anytime?",
    a: "Yes — cancel from your account settings, no questions asked. Your sites stay published until the end of the billing period.",
  },
  {
    q: "What counts as a 'site'?",
    a: "Each generated site is one site. The free plan gives you two to try. Starter and Pro are unlimited.",
  },
  {
    q: "Are visual edits and color swaps always free?",
    a: "Yes. Click-to-edit, color palette swaps, and undo are always free — on every plan, forever. That's a promise.",
  },
  {
    q: "What happens if my subscription lapses?",
    a: "Your sites display a courtesy notice to visitors. Your files stay safe in your account — reactivate and they're back live instantly.",
  },
];

// ── Components ────────────────────────────────────────────────────────────────

function Cell({ value }: { value: CellValue }) {
  if (value === true)  return <Check className="mx-auto h-4 w-4 text-primary" aria-label="Included" />;
  if (value === false) return <X    className="mx-auto h-4 w-4 text-muted-foreground/40" aria-label="Not included" />;
  return <span className="text-sm font-medium text-foreground">{value}</span>;
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function PricingPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState<PlanKey | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [sub, setSub] = useState<SubscriptionState | null | "loading">("loading");

  // Lazy-load subscription state for authenticated users.
  useState(() => {
    if (!user) { setSub(null); return; }
    fetchSubscription()
      .then(setSub)
      .catch(() => setSub(null));
  });

  async function onChoosePlan(plan: PlanKey) {
    const tier = PLANS[plan];
    if (!tier.stripePlan) {
      router.push("/workspace#phase=idea");
      return;
    }
    if (!user) {
      router.push(`/signup?redirect=/pricing`);
      return;
    }
    if (sub && sub !== "loading" && sub.status === "active") {
      router.push("/settings");
      return;
    }
    setLoading(plan);
    setError(null);
    try {
      const { url } = await createCheckoutSession(tier.stripePlan);
      window.location.href = url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
      setLoading(null);
    }
  }

  const activePlan = (sub && sub !== "loading" && sub.status === "active") ? sub.plan : null;

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-sm">
        <div className="mx-auto max-w-6xl px-6 h-14 flex items-center justify-between">
          <Link href="/landing" className="font-display text-xl font-bold tracking-tight">
            Pebble.
          </Link>
          <nav className="hidden md:flex items-center gap-6 text-sm text-muted-foreground">
            <Link href="/landing" className="hover:text-foreground transition-colors">Home</Link>
            <Link href="/pricing" className="text-foreground font-medium">Pricing</Link>
          </nav>
          <AuthMenu />
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="border-b border-border py-20 md:py-28 text-center px-6">
          <div className="mx-auto max-w-2xl space-y-4">
            <span className="text-sm font-medium uppercase tracking-wider text-primary">
              Pricing
            </span>
            <h1 className="font-display text-4xl md:text-5xl font-bold tracking-tight">
              Simple, honest pricing.
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Build for free. Pay when you're ready to go live. No
              setup fees, no annual lock-in, no surprises.
            </p>
          </div>
        </section>

        {/* Plan cards */}
        <section className="py-16 px-6 border-b border-border">
          <div className="mx-auto max-w-5xl grid grid-cols-1 md:grid-cols-3 gap-6">
            {(Object.entries(PLANS) as [PlanKey, typeof PLANS[PlanKey]][]).map(([key, plan]) => {
              const isCurrent = activePlan === plan.stripePlan;
              const isLoading = loading === key;
              return (
                <div
                  key={key}
                  className={`rounded-2xl border p-8 flex flex-col gap-6 ${
                    plan.featured
                      ? "border-primary bg-card shadow-lg"
                      : "border-border bg-card"
                  }`}
                >
                  {plan.featured && (
                    <span className="self-start text-xs font-semibold uppercase tracking-wider text-primary">
                      Most popular
                    </span>
                  )}
                  <div>
                    <h2 className="text-xl font-semibold">{plan.name}</h2>
                    <div className="mt-3 flex items-baseline gap-1">
                      <span className="font-display text-4xl font-bold">{plan.price}</span>
                      <span className="text-sm text-muted-foreground">{plan.period}</span>
                    </div>
                    <p className="mt-3 text-sm text-muted-foreground leading-relaxed">
                      {plan.description}
                    </p>
                  </div>

                  {isCurrent ? (
                    <Link
                      href="/settings"
                      className="inline-flex w-full items-center justify-center rounded-full border border-border bg-background px-4 py-2.5 text-sm font-medium text-foreground hover:bg-muted transition-colors"
                    >
                      Current plan — manage
                    </Link>
                  ) : (
                    <button
                      type="button"
                      disabled={isLoading}
                      onClick={() => onChoosePlan(key)}
                      className={`inline-flex w-full items-center justify-center rounded-full px-4 py-2.5 text-sm font-semibold transition-all disabled:opacity-60 ${
                        plan.featured
                          ? "bg-primary text-primary-foreground hover:opacity-90"
                          : "border border-border bg-background text-foreground hover:bg-muted"
                      }`}
                    >
                      {isLoading ? "Redirecting…" : plan.cta}
                    </button>
                  )}
                </div>
              );
            })}
          </div>

          {error && (
            <p className="mt-6 text-center text-sm text-destructive">{error}</p>
          )}
        </section>

        {/* Comparison table */}
        <section className="py-16 px-6 border-b border-border">
          <div className="mx-auto max-w-5xl">
            <h2 className="text-2xl font-bold tracking-tight text-center mb-10">
              Everything compared
            </h2>

            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/40">
                    <th className="py-4 px-6 text-left font-medium text-muted-foreground w-1/2">Feature</th>
                    {(["free", "starter", "pro"] as PlanKey[]).map((k) => (
                      <th key={k} className="py-4 px-4 text-center font-semibold text-foreground">
                        {PLANS[k].name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {TABLE.map((row, i) => {
                    if ("category" in row) {
                      return (
                        <tr key={i} className="border-b border-border bg-muted/20">
                          <td colSpan={4} className="py-3 px-6 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                            {row.category}
                          </td>
                        </tr>
                      );
                    }
                    return (
                      <tr key={i} className="border-b border-border last:border-0 hover:bg-muted/10 transition-colors">
                        <td className="py-3.5 px-6 text-foreground">{row.label}</td>
                        <td className="py-3.5 px-4 text-center"><Cell value={row.free} /></td>
                        <td className="py-3.5 px-4 text-center"><Cell value={row.starter} /></td>
                        <td className="py-3.5 px-4 text-center"><Cell value={row.pro} /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-16 px-6 border-b border-border">
          <div className="mx-auto max-w-2xl">
            <h2 className="text-2xl font-bold tracking-tight text-center mb-10">
              Common questions
            </h2>
            <div className="space-y-6">
              {FAQ.map((item) => (
                <div key={item.q}>
                  <h3 className="font-semibold text-foreground mb-1">{item.q}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{item.a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer CTA */}
        <section className="py-20 px-6 text-center">
          <div className="mx-auto max-w-xl space-y-4">
            <h2 className="font-display text-3xl font-bold tracking-tight">
              Start building for free.
            </h2>
            <p className="text-muted-foreground">
              No card required. Takes about 2 minutes.
            </p>
            <Link
              href="/workspace#phase=idea"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground hover:opacity-90 transition-opacity"
            >
              Build my site →
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}
